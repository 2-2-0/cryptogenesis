# Bio Chain Micro Web Server - a MWS for the biochain ledger system
# code by 220 for MP, IV & JG | 2022

import datetime
import sqlite3

from http.server import HTTPServer, BaseHTTPRequestHandler

class MicroWebServer (BaseHTTPRequestHandler):
    def do_GET (self):
        chain_storage = sqlite3.connect ("bio-chain.db")
        sql = chain_storage.cursor ()

        total_blocks = sql.execute ("SELECT COUNT (*) FROM blocks;").fetchone () [0]

        self.send_response (200)
        self.send_header ("Content-type", "text/html")
        self.end_headers ()

        self.wfile.write (bytes ("<html><head><title>cryptogenesis</title>", "utf-8"))
        self.wfile.write (bytes ("<meta http-equiv=\"refresh\" content=\"10\">", "utf-8"))
        self.wfile.write (bytes ("<style>body {background-color: #202020;color: #e0e0e0;font-family: monospace;font-size: x-small;}h1 {color: #f0fff0;}#block-chain {position: relative;width: 100%;}.block {background-color: #608060;display: inline-block;float: left;padding: 6px 6px 6px 6px;margin: 2vh 2vw 2vh 2vw;border: #507050 medium solid;box-shadow: 2px 2px #000000;}</style>", "utf-8"))
        self.wfile.write (bytes ("</head>", "utf-8"))
        self.wfile.write (bytes ("<h1>cryptogenesis</h1>", "utf-8"))
        self.wfile.write (bytes ("Total blocks: {0}<br />".format (total_blocks), "utf-8"))

        self.wfile.write (bytes ("Recent transactions:", "utf-8"))

        rows = sql.execute ("SELECT * FROM blocks ORDER BY block_id DESC LIMIT 36;").fetchall ()

        self.wfile.write (bytes ("<div id=\"block-chain\">", "utf-8"))
        for row in rows:
            self.wfile.write (bytes ("<div class=\"block\">", "utf-8"))
            self.wfile.write (bytes ("{0}. {1} [{2}/{3}] {4}<br />".format (row [0], row [2], row [7], row [8], row [3]), "utf-8"))
            self.wfile.write (bytes ("{0}<br />{1}<br />".format (row [6], row [1]), "utf-8"))
            self.wfile.write (bytes ("</div>", "utf-8"))

        self.wfile.write (bytes ("</div>", "utf-8"))

        self.wfile.write (bytes ("</body></html>", "utf-8"))


        # self.wfile.write (bytes ("", "utf-8"))

host_name = "localhost"
server_port = 8036

if __name__ == "__main__":
    web_io = HTTPServer ((host_name, server_port), MicroWebServer)

    try:
        web_io.serve_forever ()
    except KeyboardInterrupt:
        pass

    web_io.server_close ()
