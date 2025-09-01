## Giz
_A drop in, ai-powered `git commmit` replacement._

#### `giz commit` is exactly the same as `git commit`:
Except it AI-generates a commit message when no `-m` or `--message` argument is passed.  
- Confirmation is required before comitting, `-y` or `--yes` skips confirmation.  
- All extra args are passed to the underlying `git commit` call, it otherwise behaves identically.

#### Easy to modify system prompt:
Prompt is stored in a file located at: `giz prompfile`.  
The result of `git diff --staged` is pasted two newlines below whatever you put in this file.  
The default prompt is: `Generate me a very concise, short commit message from the following git diff:`