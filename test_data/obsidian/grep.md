---
---

```bash
grep -rin --include \*.ts --exclude-dir=node_modules "something to look for" ./
```

-r = recursive
-i = ignore-case
-n = include line number

find a package.json fle with the specific text in it
``` shell
grep -rin --include package.json --exclude-dir=node_modules "1.4.1" ./
```