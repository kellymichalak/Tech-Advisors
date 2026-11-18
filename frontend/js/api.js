const API_BASE_URL = "http://127.0.0.1:8000";

async function apiRequest(endpoint, method = "GET", data = null) {
   const config = {
       method: method,
       headers: {
           "Content-Type": "application/json"
       }
   };

   if (data && (method === "POST" || method === "PUT")) {
       config.body = JSON.stringify(data);
   }

   try {
       const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

       if (!response.ok) {
           const errorData = await response.json();
           throw new Error(errorData.detail || "Erro no servidor.");
       }

       if (response.status === 204) return null;

       return await response.json();
   } catch (error) {
       console.error(`[Erro na API]: ${error.message}`);
       throw error;
   }
}

export const api = {
   // Autenticação
   login: (credenciais) => apiRequest("/login", "POST", credenciais),

   // Pessoas / Usuários
   responsaveis: {
       listar: () => apiRequest("/responsaveis"),
       criar: (dados) => apiRequest("/responsaveis", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/responsaveis/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/responsaveis/${id}`, "DELETE")
   },
   professores: {
       listar: () => apiRequest("/professores"),
       criar: (dados) => apiRequest("/professores", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/professores/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/professores/${id}`, "DELETE")
   },
   alunos: {
       listar: () => apiRequest("/alunos"),
       criar: (dados) => apiRequest("/alunos", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/alunos/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/alunos/${id}`, "DELETE")
   },

   // Gestão Acadêmica
   turmas: {
       listar: (idProfessor = null) => {
           const url = idProfessor ? `/turmas?id_professor=${idProfessor}` : "/turmas";
           return apiRequest(url);
       },
       criar: (dados) => apiRequest("/turmas", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/turmas/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/turmas/${id}`, "DELETE")
   },

   // Auxiliares e Acessibilidade
   tiposDeficiencia: {
       listar: () => apiRequest("/tipos-deficiencia"),
       criar: (dados) => apiRequest("/tipos-deficiencia", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/tipos-deficiencia/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/tipos-deficiencia/${id}`, "DELETE")
   },
   niveisSuporte: {
       listar: () => apiRequest("/niveis-suporte"),
       criar: (dados) => apiRequest("/niveis-suporte", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/niveis-suporte/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/niveis-suporte/${id}`, "DELETE")
   },
   tiposAtividade: {
       listar: () => apiRequest("/tipos-atividade"),
       criar: (dados) => apiRequest("/tipos-atividade", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/tipos-atividade/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/tipos-atividade/${id}`, "DELETE")
   },
   recursosAcessibilidade: {
       listar: () => apiRequest("/recursos-acessibilidade"),
       criar: (dados) => apiRequest("/recursos-acessibilidade", "POST", dados),
       atualizar: (id, dados) => apiRequest(`/recursos-acessibilidade/${id}`, "PUT", dados),
       deletar: (id) => apiRequest(`/recursos-acessibilidade/${id}`, "DELETE")
   }
};