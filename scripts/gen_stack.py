import json
import pathlib

VOID, PANEL = '#05070A', '#0A0E14'
BLUE, CYAN = '#1F6FEB', '#58C4FF'
ICON = '#6E9BD8'      # tom dos icones: familia do azul, legivel sobre preto
BODY = '#C9D1D9'
DIM = '#6E7681'
MONO = ('ui-monospace, SFMono-Regular, &#34;SF Mono&#34;, Menlo, Consolas, '
        '&#34;Liberation Mono&#34;, monospace')

BRAND = json.loads(pathlib.Path('icons.json').read_text())
# cores oficiais das marcas, ja com contraste garantido sobre o fundo escuro
COLORS = json.loads(pathlib.Path('colors.json').read_text())
# conceitos (sem marca) ficam no azul de acento, criando uma regra clara de leitura
CONCEPT = CYAN
OUT = pathlib.Path('out')
OUT.mkdir(exist_ok=True)

# ── glifos proprios (24x24, tracejados) para o que nao tem logo ──
# conceitos de IA e marcas que a simple-icons nao distribui mais
SW = 'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"'

GLYPH = {
    # faisca: IA generativa
    'spark': f'<path d="M12 3v6M12 15v6M3 12h6M15 12h6M6.4 6.4l3 3M14.6 14.6l3 3M17.6 6.4l-3 3M9.4 14.6l-3 3" {SW}/>',
    # camadas: LLMs
    'layers': f'<path d="M12 3.5 3.5 8 12 12.5 20.5 8 12 3.5ZM3.5 12.4 12 16.9l8.5-4.5M3.5 16.6 12 21l8.5-4.4" {SW}/>',
    # prompt: engenharia de prompt
    'prompt': f'<path d="M4.5 4.5h15v15h-15zM8 10l2.4 2.4L8 14.8M13 15h3" {SW}/>',
    # agente: hexagono com nucleo
    'agent': f'<path d="M12 2.8l7.6 4.4v8.8L12 20.4 4.4 16V7.2ZM12 9.4a2.6 2.6 0 1 0 0 5.2 2.6 2.6 0 0 0 0-5.2Z" {SW}/>',
    # ciclo: automacao que roda em loop (evita parecer com o grafo do n8n)
    'flow': f'<path d="M3.8 12a8.2 8.2 0 0 1 14-5.8" {SW}/>'
            f'<path d="M13.9 6.2h3.9V2.3" {SW}/>'
            f'<path d="M20.2 12a8.2 8.2 0 0 1-14 5.8" {SW}/>'
            f'<path d="M10.1 17.8H6.2v3.9" {SW}/>',
    # linguagem natural
    'nlp': f'<path d="M3.6 5.4h16.8v10.2H12l-4.6 3.6v-3.6H3.6zM7.2 8.8h9.6M7.2 12h6" {SW}/>',
    # banco de dados
    'db': f'<path d="M12 2.9c4.2 0 7.3 1.2 7.3 2.7S16.2 8.3 12 8.3 4.7 7.1 4.7 5.6 7.8 2.9 12 2.9Z'
          f'M4.7 5.6v12.8c0 1.5 3.1 2.7 7.3 2.7s7.3-1.2 7.3-2.7V5.6M4.7 12c0 1.5 3.1 2.7 7.3 2.7'
          f's7.3-1.2 7.3-2.7" {SW}/>',
    # ajuste de consulta: banco + controle
    'dbtune': f'<path d="M11 2.9c4 0 7 1.2 7 2.7S15 8.3 11 8.3 4 7.1 4 5.6 7 2.9 11 2.9Z'
              f'M4 5.6v9.6c0 1.5 3 2.7 7 2.7M4 11.4c0 1.5 3 2.7 7 2.7" {SW}/>'
              f'<path d="M14.4 20.4v-4.8M18.6 20.4v-2.6M12.8 17.4h3.2M17 15.6h3.2" {SW}/>',
    # analise de dados
    'chart': f'<path d="M4 20.2h16M7 20.2v-6.4M11.6 20.2V6.6M16.2 20.2v-9.4M20.4 20.2V9" {SW}/>',
    # API REST
    'api': f'<path d="M9 5.4 5.2 9.2 9 13M15 11l3.8 3.8L15 18.6M12.6 4.6 10.4 19.4" {SW}/>',
    # C# (logo nao distribuido pela simple-icons: monta o C + sustenido)
    'csharp': f'<path d="M14.6 6.9a6.4 6.4 0 1 0 0 10.2" {SW}/>'
              f'<path d="M17.9 8.1l-.8 7.8M21.1 8.1l-.8 7.8M16.2 10.9h5.4M15.9 13.5h5.4" {SW}/>',
    # janela de terminal
    'terminal': f'<path d="M3.4 4.6h17.2v14.8H3.4zM3.4 8.4h17.2M6.6 12.2l2.2 2.2-2.2 2.2M11.4 16.6h4" {SW}/>',
    # 4 painéis
    'window': f'<path d="M4 4.8h6.8v6.4H4zM13.2 4.8H20v6.4h-6.8zM4 12.8h6.8v6.4H4zM13.2 12.8H20v6.4h-6.8z" {SW}/>',
    # robo: plataforma de chatbot
    'bot': f'<rect x="5.2" y="7.8" width="13.6" height="10.6" rx="3.2" {SW}/>'
           f'<path d="M12 7.8V5.2" {SW}/>'
           f'<circle cx="12" cy="3.9" r="1.3" {SW}/>'
           f'<circle cx="9.5" cy="12.8" r="1.35" fill="currentColor" stroke="none"/>'
           f'<circle cx="14.5" cy="12.8" r="1.35" fill="currentColor" stroke="none"/>',
}


def icon(kind, x, y, size=14):
    """Coloca um icone de 24x24 escalado, com o canto superior esquerdo em (x, y)."""
    s = size / 24
    if kind in BRAND:
        inner = f'<path d="{BRAND[kind]["path"]}" fill="currentColor"/>'
    elif kind in GLYPH:
        inner = GLYPH[kind]
    else:
        raise KeyError(f'icone desconhecido: {kind}')
    color = COLORS.get(kind, CONCEPT)
    return (f'<g transform="translate({x} {y}) scale({s:.5f})" color="{color}">'
            f'{inner}</g>')


COLS = [
    ('ARTIFICIAL INTELLIGENCE', [
        ('spark', 'Generative AI'), ('layers', 'LLMs'),
        ('prompt', 'Prompt Engineering'), ('agent', 'AI Agents'),
        ('flow', 'AI Workflows'), ('nlp', 'NLP'),
        ('gemini', 'Google Gemini'), ('ollama', 'Ollama'),
        ('n8n', 'n8n'), ('bot', 'Botpress')]),
    ('LANGUAGES / FRAMEWORKS', [
        ('php', 'PHP'), ('laravel', 'Laravel'), ('javascript', 'JavaScript'),
        ('typescript', 'TypeScript'), ('react', 'React'), ('vue', 'Vue.js'),
        ('html5', 'HTML5'), ('css3', 'CSS3'), ('csharp', 'C#'),
        ('cpp', 'C / C++'), ('dotnet', 'ASP.NET Core')]),
    ('DATA', [
        ('mysql', 'MySQL'), ('db', 'SQL Server'), ('supabase', 'Supabase'),
        ('dbtune', 'Query tuning'), ('chart', 'Data analysis')]),
    ('DEVOPS / TOOLS', [
        ('git', 'Git'), ('github', 'GitHub'), ('docker', 'Docker'),
        ('api', 'REST APIs'), ('postman', 'Postman'), ('swagger', 'Swagger'),
        ('linux', 'Linux'), ('window', 'Windows'), ('bash', 'Bash'),
        ('terminal', 'PowerShell')]),
]

W = 1000
PAD_X, TOP = 46, 44
COL_W = (W - PAD_X * 2) // 4
LINE_H = 23
rows_max = max(len(i) for _, i in COLS)
H = TOP + 32 + rows_max * LINE_H + 10

body = []
for i, (head, items) in enumerate(COLS):
    x = PAD_X + i * COL_W
    body.append(f'<text x="{x}" y="{TOP}" font-family="{MONO}" font-size="10.5" '
                f'letter-spacing="1.7" fill="{BLUE}" font-weight="700">{head}</text>')
    body.append(f'<rect x="{x}" y="{TOP+10}" width="{COL_W-30}" height="1.4" '
                f'fill="{BLUE}" fill-opacity="0.45"/>')
    for j, (kind, label) in enumerate(items):
        y = TOP + 36 + j * LINE_H
        body.append(icon(kind, x, y - 11))
        body.append(f'<text x="{x+22}" y="{y}" font-family="{MONO}" font-size="12.4" '
                    f'fill="{BODY}">{label}</text>')


def brackets(x, y, w, h, off=9, arm=20, sw=2):
    c = [(x-off, y-off, 1, 1), (x+w+off, y-off, -1, 1),
         (x-off, y+h+off, 1, -1), (x+w+off, y+h+off, -1, -1)]
    return '\n  '.join(
        f'<path d="M {bx+dx*arm} {by} H {bx} V {by+dy*arm}" fill="none" '
        f'stroke="{BLUE}" stroke-width="{sw}" stroke-linecap="square"/>'
        for bx, by, dx, dy in c)


svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-label="Stack tecnica de Erick Silva Ramos da Paz">
  <title>Stack</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{VOID}"/>
    </linearGradient>
    <pattern id="raster" width="4" height="3" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="{CYAN}"/>
    </pattern>
  </defs>
  <rect x="0.75" y="0.75" width="{W-1.5}" height="{H-1.5}" rx="14"
        fill="url(#bg)" stroke="{BLUE}" stroke-opacity="0.26" stroke-width="1.5"/>
  <rect x="{PAD_X}" y="22" width="{W-PAD_X*2}" height="{H-44}" fill="url(#raster)" opacity="0.045"/>
  {brackets(PAD_X-8, 22, W-PAD_X*2+16, H-42)}
{chr(10).join('  ' + b for b in body)}
</svg>
'''
(OUT / 'stack.svg').write_text(svg, encoding='utf-8')
print('stack.svg', (OUT / 'stack.svg').stat().st_size, 'bytes', f'({W}x{H})')
