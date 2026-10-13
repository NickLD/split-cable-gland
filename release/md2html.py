"""Tiny Markdown -> HTML for description.md (headings, lists, bold, code, links)."""
import html, re, sys

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s

def convert(md):
    out, lst = [], None
    def close():
        nonlocal lst
        if lst:
            out.append("</%s>" % lst)
            lst = None
    for line in md.splitlines():
        if not line.strip():
            close(); continue
        m = re.match(r"(#{1,3}) (.*)", line)
        if m:
            close(); out.append("<h%d>%s</h%d>" % (len(m.group(1)) + 1, inline(m.group(2)), len(m.group(1)) + 1)); continue
        m = re.match(r"- (.*)", line)
        if m:
            if lst != "ul": close(); out.append("<ul>"); lst = "ul"
            out.append("<li>%s</li>" % inline(m.group(1))); continue
        m = re.match(r"\d+\. (.*)", line)
        if m:
            if lst != "ol": close(); out.append("<ol>"); lst = "ol"
            out.append("<li>%s</li>" % inline(m.group(1))); continue
        close(); out.append("<p>%s</p>" % inline(line))
    close()
    return "".join(out)

if __name__ == "__main__":
    md = open(sys.argv[1], encoding="utf-8").read().split("\n", 2)[2]   # drop the title line
    print(convert(md))
