## Giz
_Drop in `git commit` replacement with AI commit message._  
  
Have any suggestions, or errors? Please send me an email! jake@burla.dev

### `giz commit` behaves exactly like `git commit`
With one exception: The commit message is AI generated when no `-m` or `--message` argument is passed.
- Confirmation is required before committing, use `-y` or `--yes` to skip confirmation.  
- All other args are passed to the underlying `git commit` call, it's behavior is otherwise identical.

### Easy to modify system prompt:
Prompt is stored in a textfile located at: `giz prompfile`.  
The diff (`git diff --staged`) is pasted two newlines below whatever you put in this file.  

### Quickstart:

- `pip install giz`
- `giz set_openai_api_key <your-api-key>`
- `giz commit ...`

### Demo:
<figure><img src="./demo.gif" alt="" style="width:100%" /></figure>
