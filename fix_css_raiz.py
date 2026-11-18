# 1. Corrigir o comentário e seletor universal quebrados no topo do admin.css + forçar coluna no dropdown
css_path = "frontend/css/admin.css"
css = open(css_path, encoding="utf-8").read()

css = css.replace("- ==================== ESTILOS GLOBAIS ==================== */", "/* ==================== ESTILOS GLOBAIS ==================== */")
css = css.replace("\n- {\n", "\n* {\n", 1)

# Impedir que 'nav ul' force flex-direction: row dentro do .user-dropdown
css = css.replace(
"""nav ul {
display: flex;
flex-direction: row;
align-items: center;
list-style: none;
gap: 25px;
}""",
"""nav > ul {
display: flex;
flex-direction: row;
align-items: center;
list-style: none;
gap: 22px;
}
.user-dropdown {
position: absolute;
right: 0;
top: calc(100% + 10px);
min-width: 210px;
background: #ffffff;
border-radius: 14px;
box-shadow: 0 12px 30px rgba(15, 23, 42, 0.18);
border: 1px solid #e2e8f0;
padding: 6px;
z-index: 999;
}
.user-dropdown ul {
display: flex !important;
flex-direction: column !important;
align-items: stretch !important;
gap: 4px !important;
list-style: none !important;
padding: 0 !important;
margin: 0 !important;
}
.user-dropdown li {
display: flex !important;
align-items: center !important;
gap: 10px !important;
padding: 10px 14px !important;
border-radius: 10px !important;
color: #1e293b !important;
font-size: 14px !important;
font-weight: 600 !important;
white-space: nowrap !important;
}
.user-dropdown li:hover {
background: #eff6ff !important;
color: #1d4ed8 !important;
}
.user-dropdown li.logout-item {
color: #dc2626 !important;
border-top: 1px solid #f1f5f9 !important;
margin-top: 4px !important;
padding-top: 10px !important;
}
.user-dropdown li.logout-item:hover {
background: #fef2f2 !important;
color: #b91c1c !important;
}
body.dark-theme .user-dropdown {
background: #1e1b4b !important;
border-color: #312e81 !important;
}
body.dark-theme .user-dropdown li {
color: #f1f5f9 !important;
}
body.dark-theme .user-dropdown li:hover {
background: #312e81 !important;
color: #fde047 !important;
}"""
)

open(css_path, "w", encoding="utf-8").write(css)

# 2. Atualizar versão do CSS para v=8 em todas as páginas do Admin
import os
for page in [
    "frontend/pages/admin.html",
    "frontend/pages/cadastro-turmas.html",
    "frontend/pages/cadastro-alunos.html",
    "frontend/pages/cadastro-professores.html",
    "frontend/pages/relatorios-admin.html",
]:
    if os.path.exists(page):
        h = open(page, encoding="utf-8").read()
        h = h.replace("admin.css?v=7", "admin.css?v=8").replace("admin.js?v=7", "admin.js?v=8")
        open(page, "w", encoding="utf-8").write(h)

print("CSS_RAIZ_E_DROPDOWN_CORRIGIDOS_OK")
