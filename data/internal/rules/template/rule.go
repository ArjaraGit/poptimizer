package template

import (
	"context"
	"sync"
	"time"

	"github.com/WLM1ke/poptimizer/data/internal/domain"
	"github.com/WLM1ke/poptimizer/data/internal/repo"
	"github.com/WLM1ke/poptimizer/data/pkg/lgr"
)

// Rule - шаблон правила по обновлению большинства таблиц.
type Rule[R domain.Row] struct { //nolint:varnamelen
	name      string
	logger    *lgr.Logger
	repo      repo.ReadWrite[R]
	selector  Selector
	gateway   Gateway[R]
	validator Validator[R]
	append    bool
	timeout   time.Duration
}

// NewRule создает правило на основе шаблона.
func NewRule[R domain.Row]( //nolint:varnamelen
	name string,
	logger *lgr.Logger,
	repo repo.ReadWrite[R],
	selector Selector,
	gateway Gateway[R],
	validator Validator[R],
	appendRows bool,
	timeout time.Duration,
) Rule[R] {
	return Rule[R]{
		name:      name,
		logger:    logger,
		repo:      repo,
		selector:  selector,
		gateway:   gateway,
		validator: validator,
		append:    appendRows,
		timeout:   timeout,
	}
}

// Activate шаблонное правило.
func (r Rule[R]) Activate(inbox <-chan domain.Event) <-chan domain.Event {
	out := make(chan domain.Event)

	go func() {
		r.logger.Infof("%s: started", r.name)
		defer r.logger.Infof("%s: stopped", r.name)

		defer close(out)

		var wg sync.WaitGroup
		defer wg.Wait()

		for event := range inbox {
			wg.Add(1)

			event := event

			go func() {
				defer wg.Done()

				r.handleEvent(out, event)
			}()
		}
	}()

	return out
}

func (r Rule[R]) handleEvent(out chan<- domain.Event, event domain.Event) {
	ctx, cancel := context.WithTimeout(context.Background(), r.timeout)
	defer cancel()

	var wg sync.WaitGroup
	defer wg.Wait()

	ids, err := r.selector.Select(ctx, event)
	if err != nil {
		out <- domain.NewErrorOccurred(event.ID(), err)

		return
	}

	for _, id := range ids {
		wg.Add(1)

		id := id

		go func() {
			defer wg.Done()

			if newEvent := r.handleUpdate(ctx, id); newEvent != nil {
				out <- newEvent
			}
		}()
	}
}

func (r Rule[R]) handleUpdate(ctx context.Context, id domain.ID) domain.Event { //nolint:ireturn
	table, err := r.repo.Get(ctx, id)
	if err != nil {
		return domain.NewErrorOccurred(id, err)
	}

	rows, err := r.gateway.Get(ctx, table)
	if err != nil {
		return domain.NewErrorOccurred(id, err)
	}

	if !r.haveNewRows(rows) {
		return nil
	}

	err = r.validator(table, rows)
	if err != nil {
		return domain.NewErrorOccurred(id, err)
	}

	if r.append {
		err = r.repo.Append(ctx, domain.NewTable(id, time.Now(), rows[1:]))
	} else {
		err = r.repo.Replace(ctx, domain.NewTable(id, time.Now(), rows))
	}

	if err != nil {
		return domain.NewErrorOccurred(id, err)
	}

	return domain.NewUpdateCompleted(id)
}

func (r Rule[R]) haveNewRows(rows []R) bool {
	if len(rows) == 0 {
		return false
	}

	if r.append && (len(rows) == 1) {
		return false
	}

	return true
}
