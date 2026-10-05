# Points of disagreement and alternative approaches

## Error wrapping libraries

Sources disagree on error library choice:

- **Standard library**: Google recommends `fmt.Errorf` with `%w`
- **pkg/errors**: Thanos prefers explicit `errors.Wrap`
- **cockroachdb/errors**: CockroachDB uses their own superset with redaction
  support

The consensus: use *some* form of wrapping; the specific library matters less
than consistent application.

## Project structure

- **Peter Bourgon (2016)**: Recommended cmd/pkg structure
- **Peter Bourgon (2018)**: Softened stance—start simple, add structure only
  when needed
- **Google**: No prescribed structure; organize by maintainability

The consensus: avoid premature structure, but cmd/pkg works when complexity
warrants it.

## Test assertions

- **Google**: Forbids assertion libraries; use standard testing package
- **GitLab**: Permits testify for assertions
- **Peter Bourgon**: Testing DSLs increase cognitive burden

The consensus: the standard library suffices; third-party frameworks are
optional convenience.

## Receiver type consistency

- **Google Code Review Comments**: Don't mix receiver types on one type
- **Effective Go**: Choose based on method needs

Practical guidance: if any method needs a pointer receiver (mutation, large
struct, sync primitives), use pointer receivers for all methods on that type.
