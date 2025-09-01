## Giz
_Drop in `git commit` replacement with AI commit message._

### `giz commit` is exactly the same as `git commit`:
Except it AI-generates a commit message when no `-m` or `--message` argument is passed.  
- Confirmation is required before comitting, `-y` or `--yes` skips confirmation.  
- All other args are passed to the underlying `git commit` call, it's behaivior is otherwise identical.

### Easy to modify system prompt:
Prompt is stored in a textfile located at: `giz prompfile`.  
The diff (`git diff --staged`) is pasted two newlines below whatever you put in this file.  
Default prompt: `Generate me a very concise, short commit message from the following git diff:`


### Quickstart:

- `pip install giz`
- `giz set_openai_api_key <your-api-key>`
- `giz commit ...`

### Demo:
<figure><img src="./demo.gif" alt="" style="width:100%" /></figure>
