---
alias: bash commands, terminal commands
---

keywords: unix, linux, bash, shell

[[grep]]
[[ack]]
[[find]]
[[tmux]]
[[SSH reference]]

get linux distribution info
```shell
cat /etc/os-release
```

add directory to path
```shell
export PATH="$HOME/bin:$PATH"
```

zip folder
```shell
zip -r myfiles.zip mydir
```

unzip
```shell
unzip file.zip -d destination_dir
```

find out which shell I am running
``` shell
ps -p $$
```

recursively delete all files with a certain extension
```shell
find . -type f -name '*.log' -delete
```

list all directories with specified name recursively
- the prune flag removes matched directories that have the name in the path but are not the actual directory
```shell
find . -name 'node_modules' -type d -prune
```

delete all node_modules folders recursively
```shell
find . -name 'node_modules' -type d -prune -exec rm -rf '{}' +
```

download files from a web directory recursively
```shell
wget --recursive --no-parent http://example.com/configs/.vim/
```

repeat curl with delay
```shell
for i in `seq 1 10000`; do curl http://localhost:8181; sleep 1; done
```

base64 a string on command-line
`echo -n somepassword | base64`

[50 macOS Tips and Tricks Using Terminal (the last one is CRAZY!) - YouTube](https://www.youtube.com/watch?v=qOrlYzqXPa8)
`caffeinate` will prevent computer from going to sleep

take JS code, minify it, compress it, and count number of bytes
```shell
alias jssize="pbpaste | terser - c - m | gzip - c9n | wc - c" 
```

get size of directory
```shell
du -h /path
```

copy contents of a file to clipboard
```shell
pbcopy < filename
```