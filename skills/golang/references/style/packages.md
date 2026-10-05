# Code organization emerges from simplicity

## Start small and add structure only when needed

Peter Bourgon advises: **"Most projects start as a few files in package main at
the root, staying that way until they become a couple thousand lines."** Go's
lightweight feel should be preserved. Rigid a priori project structure typically
harms more than helps—requirements diverge, grow, and mutate.

When structure becomes necessary, the `cmd/pkg` layout works well for
applications with multiple binaries:

```text
github.com/yourorg/project/
    cmd/
        server/
            main.go
        cli/
            main.go
    pkg/
        storage/
            storage.go
            storage_test.go
        api/
            api.go
```

## Packages should fulfill a single purpose

Create packages when you have self-contained functionality, need protobuf
definitions, find a package grown too large (slow tests, insufficient
encapsulation), or have reusable code another team needs. Orient packages around
**business domains rather than implementation accidents**—prefer `package user`
over `package models`.

Google's guidance on file organization: **"There is no 'one type, one file'
convention."** Files should be focused enough that maintainers know where to
find things, and small enough to navigate easily. The standard library's
`net/http` package demonstrates this: `client.go`, `server.go`, `cookie.go`,
`transport.go`.

## Import grouping follows a standard order

Separate imports into groups: standard library, external dependencies, internal
packages:

```go
import (
    "context"
    "fmt"
    "time"

    "github.com/pkg/errors"
    "go.uber.org/zap"

    "github.com/yourorg/project/pkg/storage"
)
```

Always use fully-qualified import paths, never relative imports. GitLab enforces
this with `goimports -local gitlab.com/gitlab-org`.
