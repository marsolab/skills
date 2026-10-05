# Foundational principles that shape every guideline

Go's design philosophy flows from a single insight: **"Software engineering is
what happens to programming when you add time and other programmers."** Code
will be read far more than written, maintained by people who didn't write it,
and debugged under pressure at 3 AM. Every guideline here serves readability and
maintainability.

The Zen of Go, articulated by Dave Cheney, captures ten engineering values that
should guide decisions:

1. **Each package fulfills a single purpose**—name it with an elevator pitch
  using one word
1. **Handle errors explicitly**—the verbosity of `if err != nil` outweighs the
  value of deliberately handling each failure
1. **Return early rather than nesting deeply**—keep the success path to the left
1. **Leave concurrency to the caller**—don't force async on consumers
1. **Before launching a goroutine, know when it will stop**—goroutines own
  resources
1. **Avoid package-level state**—reduce coupling and spooky action at a distance
1. **Simplicity matters**—simple doesn't mean crude; it means readable and
  maintainable
1. **Write tests to lock in API behavior**—tests are contracts written in code
1. **Prove slowness with benchmarks before optimizing**—crimes against
  maintainability are committed in the name of performance
1. **Moderation is a virtue**—use goroutines, channels, interfaces in moderation
