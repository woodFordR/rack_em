# RACK_EM, A HTTP Server Written in Python Using *[uv](https://docs.astral.sh/uv/)*

---
## Useful Commands
  - ```uvx migrate-to-uv```
  - ```uv sync --dev```
  - ```uv run src/rack_em/main.py```
  - ```uv python pin 3.13.5```
  - ```uv venv -p 3.13.5```
  - ```source .venv/bin/activate```

---
## Testing With *[curl](https://curl.se/)*
  - ```curl -v http://localhost:3000```
  - ```curl -v http://localhost:3000/university```
  - ```curl -v http://localhost:3000/echo/woodford```
  - ```curl -v --header "User-Agent: exercise/1.2.3" http://localhost:3000/user-agent```
  - ```nc localhost 3000``` && ```curl -v localhost:3000```
  - ```echo -n 'let us hike and camp this weekend' > src/rack_em/data/files/camping``` && 
    ```curl -i http://localhost:3000/files/camping```
  - ```curl -i http://localhost:3000/files/my_vacant_file```
  - ```./your_program.sh --directory **/**/files/```
  - ```curl -v --data "440000" -H "Content-Type: application/octet-stream" http://localhost:3000/files/file_217```
  - ```curl -v -H "Accept-Encoding: gzip" http://localhost:3000/echo/tictac```
  - ```curl -v -H "Accept-Encoding: horrible-encoding" http://localhost:3000/echo/gum```
  - ```curl -v -H "Accept-Encoding: nonsense-encoding-1, gzip, awful-encoding-2" http://localhost:3000/echo/kentucky```
  - ```curl -v -H "Accept-Encoding: terrible-encoding-1, nonsense-encoding-2" http://localhost:3000/echo/jersey```
  - ```curl -v -H "Accept-Encoding: gzip" http://localhost:3000/echo/volleyball | hexdump -C```
  - ```curl --http1.1 -v http://localhost:3000/echo/strawberry --next http://localhost:3000/user-agent -H "User-Agent: kiwi/peach-kiwi"```
  - ```curl --http1.1 -v http://localhost:3000/user-agent -H "User-Agent: vanilla/cranberry-lime" --next http://localhost:3000/echo/sushi```
  - ```curl --http1.1 -v http://localhost:3000/echo/aqua-green --next http://localhost:3000/ -H "Connection: close"```

---
## Response Breakdown
  - >**Status Line**
    - >>HTTP/1.1 `HTTP version`
    - >>200 `Status code`
    - >>OK `Optional reason phrase`
    - >>\r\n `CRLF that marks the end of the status line`

  - >**Headers**
    - >>\r\n `CRLF that marks the end of the headers`

  - >**Response Body**

---
## Links

  - [HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) 
  - [HTTP request syntax](https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html)

