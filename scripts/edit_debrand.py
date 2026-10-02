#!/usr/bin/env python3
"""Remove visible "Tatler" branding from The Edit site (ES pages + EN tatler/ dir): text nodes, alt/title/aria-label,
<title> and og/twitter/description meta. URLs, class names (font-tatler), scripts and styles are untouched.
Usage: python edit_debrand.py [repo]   (build_site.py calls debrand_repo() after every build)"""
import glob, os, re, sys
PHRASES = [(r"\s*[–-]\s*follow @tatler\w* across social media for the latest updates\.", "."), (r"@tatler\w*", "The Edit"), (r"theditrevista\.vercel\.app/tatler/?", "theditrevista.vercel.app"), (r"Stories sourced from Tatler\.com", "Stories curated by The Edit"), (r"\bTatler uses\b", "The Edit uses"),
           (r"\bTatler\.com\b", "The Edit"), (r"\bTatler(?:\s*·\s*|\s+)English\b", "Edit English")]
W = re.compile(r"\btatler\b", re.I)
def sub(t):
    for a, b in PHRASES: t = re.sub(a, b, t)
    return W.sub(lambda m: "EDIT" if m.group(0).isupper() else ("Edit" if m.group(0)[0].isupper() else "edit"), t)
def text_sub(t):
    return sub(t)
SKIP = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->)", re.S | re.I)
def fix(seg):
    seg = re.sub(r">([^<]+)<", lambda m: ">" + text_sub(m.group(1)) + "<", seg)
    seg = re.sub(r'(\s(?:alt|title|aria-label|placeholder)=")([^"]*)"', lambda m: m.group(1) + sub(m.group(2)) + '"', seg)
    seg = re.sub(r'(<meta[^>]+(?:property|name)="(?:og:title|og:description|og:site_name|twitter:title|twitter:description|description)"[^>]*content=")([^"]*)"',
                 lambda m: m.group(1) + sub(m.group(2)) + '"', seg)
    return seg
def debrand_html(s):
    return "".join(p if SKIP.fullmatch(p) else fix(p) for p in SKIP.split(s))
def debrand_repo(repo):
    n = 0
    for f in glob.glob(os.path.join(str(repo), "**", "*.html"), recursive=True):
        if os.sep + "newsletter" + os.sep in f: continue
        s = open(f, encoding="utf-8").read(); new = debrand_html(s)
        if new != s: open(f, "w", encoding="utf-8").write(new); n += 1
    return n
if __name__ == "__main__":
    print("edit_debrand:", debrand_repo(sys.argv[1] if len(sys.argv) > 1 else "/workspace/theditrevista"), "files changed")
