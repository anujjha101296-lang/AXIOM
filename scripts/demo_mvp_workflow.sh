#!/usr/bin/env bash
# Demo: Complete MVP-0 researcher workflow (register → login → research → resume)
set -euo pipefail

API="${API_URL:-http://localhost:8000}"
EMAIL="${DEMO_EMAIL:-researcher.demo@axiom.local}"
PASSWORD="${DEMO_PASSWORD:-axiom-demo-pass}"
NAME="${DEMO_NAME:-Demo Researcher}"

echo "=== AXIOM MVP-0 Complete Workflow Demo ==="
echo "API: $API"
echo "User: $EMAIL"
echo

echo "1. Register account (or sign in if already exists)..."
REGISTER_RES=$(curl -s -w "\n%{http_code}" -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"name\":\"$NAME\"}")
REGISTER_CODE=$(echo "$REGISTER_RES" | tail -1)
REGISTER_BODY=$(echo "$REGISTER_RES" | head -n -1)

if [ "$REGISTER_CODE" = "201" ]; then
  TOKEN=$(echo "$REGISTER_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
  echo "   Registered new account."
elif [ "$REGISTER_CODE" = "400" ]; then
  echo "   Account exists — signing in..."
  LOGIN_RES=$(curl -sf -X POST "$API/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
  TOKEN=$(echo "$LOGIN_RES" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
else
  echo "   Register failed ($REGISTER_CODE): $REGISTER_BODY"
  exit 1
fi
AUTH="Authorization: Bearer ${TOKEN}"
echo "   Authenticated."

echo "2. Verify session (GET /auth/me)..."
curl -sf "$API/auth/me" -H "$AUTH" | python3 -c "
import sys, json
u = json.load(sys.stdin)
print(f'   Signed in as {u[\"name\"]} <{u[\"email\"]}>')
"

echo "3. Create research project..."
PROJECT=$(curl -sf -X POST "$API/research/projects" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"name":"Riemann Zeta Survey","description":"Literature review of critical line results"}')
PROJECT_ID=$(echo "$PROJECT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "   Project ID: $PROJECT_ID"

echo "4. Upload sample PDF (text extraction)..."
PDF_FILE=$(mktemp --suffix=.pdf)
python3 - "$PDF_FILE" << 'PY'
import sys

def make_text_pdf(text: str) -> bytes:
    objects = []
    def obj(content: str) -> str:
        objects.append(content)
        return str(len(objects))
    font_id = obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET"
    content_id = obj(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
    page_id = obj(
        f"<< /Type /Page /Parent 5 0 R /MediaBox [0 0 612 792] "
        f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
    )
    pages_id = obj(f"<< /Type /Pages /Kids [{page_id} 0 R] /Count 1 >>")
    catalog_id = obj(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")
    out = ["%PDF-1.4\n"]
    xref_positions = []
    for i, o in enumerate(objects, start=1):
        xref_positions.append(sum(len(x.encode("latin-1")) for x in out))
        out.append(f"{i} 0 obj\n{o}\nendobj\n")
    xref_start = sum(len(x.encode("latin-1")) for x in out)
    out.append("xref\n")
    out.append(f"0 {len(objects) + 1}\n")
    out.append("0000000000 65535 f \n")
    for pos in xref_positions:
        out.append(f"{pos:010d} 00000 n \n")
    out.append(f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n")
    out.append(f"startxref\n{xref_start}\n%%EOF\n")
    return "".join(out).encode("latin-1")

with open(sys.argv[1], "wb") as f:
    f.write(make_text_pdf("Riemann zeta function and critical line literature review."))
PY

UPLOAD_RES=$(curl -s -w "\n%{http_code}" -X POST \
  "$API/research/projects/$PROJECT_ID/documents/upload" \
  -H "$AUTH" -F "file=@${PDF_FILE};type=application/pdf")
HTTP_CODE=$(echo "$UPLOAD_RES" | tail -1)
BODY=$(echo "$UPLOAD_RES" | head -n -1)
rm -f "$PDF_FILE"

if [ "$HTTP_CODE" != "201" ]; then
  echo "   Upload failed ($HTTP_CODE): $BODY"
  exit 1
fi
DOC_ID=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
CHARS=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['char_count'])")
echo "   Document ID: $DOC_ID ($CHARS chars extracted)"

echo "5. Generate summary..."
curl -sf -X POST "$API/research/projects/$PROJECT_ID/documents/$DOC_ID/summarize" -H "$AUTH" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('   Summary:', d.get('summary','')[:120]+'...')"

echo "6. Save structured note..."
curl -sf -X POST "$API/research/projects/$PROJECT_ID/notes" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"title":"Critical line insight","body":"All non-trivial zeros of zeta(s) are conjectured to lie on Re(s)=1/2.","tags":["RH","zeta"]}' \
  > /dev/null
echo "   Note saved."

echo "7. Full-text search across papers and notes..."
curl -sf "$API/research/search?q=zeta&project_id=$PROJECT_ID" -H "$AUTH" | \
  python3 -c "import sys,json; r=json.load(sys.stdin); print(f'   Found {len(r)} result(s)'); [print(f'   - [{x[\"result_type\"]}] {x[\"title\"]}') for x in r[:3]]"

echo "8. Ask a question about the paper..."
ASK=$(curl -sf -X POST "$API/research/projects/$PROJECT_ID/ask" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"question\":\"What does this paper say about the Riemann zeta function?\",\"document_id\":\"$DOC_ID\"}")
CONV_ID=$(echo "$ASK" | python3 -c "import sys,json; print(json.load(sys.stdin)['conversation_id'])")
echo "$ASK" | python3 -c "import sys,json; a=json.load(sys.stdin); print('   Answer:', a.get('answer','')[:120]+'...')"
echo "   Conversation ID: $CONV_ID"

echo "9. Resume research session..."
curl -sf -X POST "$API/research/projects/$PROJECT_ID/sessions/resume" -H "$AUTH" | \
  python3 -c "import sys,json; s=json.load(sys.stdin); print(f'   Session resumed at {s[\"last_active_at\"]}')"

echo
echo "10. Project detail:"
curl -sf "$API/research/projects/$PROJECT_ID" -H "$AUTH" | python3 -c "
import sys, json
d = json.load(sys.stdin)
p = d['project']
print(f'   {p[\"name\"]}: {p[\"document_count\"]} documents, {p[\"note_count\"]} notes')
print(f'   Conversations: {len(d.get(\"conversations\", []))}')
print(f'   Session active: {d.get(\"session\") is not None}')
if d.get('active_conversation'):
    print(f'   Active conversation messages: {len(d[\"active_conversation\"][\"messages\"])}')
"

echo
echo "=== MVP workflow complete ==="
echo "UI: http://localhost:3000/login"
echo "Sign in with: $EMAIL / $PASSWORD"
