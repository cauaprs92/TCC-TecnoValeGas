# Claude.md - Instruções de Contexto

**Data de Criação:** 29 de Abril de 2026  
**Perfil:** Desenvolvedor Avançado | Web Apps + APIs/Backend | São Paulo, BR

---

## 🎯 Características Principais

### Tipo de Projeto
- **Foco Principal:** Web Applications (React, HTML/CSS) + APIs REST/Backend
- **Secundário:** Pode incluir automação, scripts utilitários e processamento de dados
- **Tech Stack Esperado:** Node.js, Express, React, TypeScript, PostgreSQL, MongoDB

### Estilo de Comunicação Preferido
- ✅ **Objetivo mas com contexto necessário** - não seja superficial, mas também não seja verboso
- ✅ Explicações técnicas diretas com exemplos quando relevante
- ✅ Assuma conhecimento avançado - não explique conceitos básicos
- ✅ Foque em "porquê" quando houver decisões arquiteturais

### Nível de Experiência
- 🟢 **Avançado** - compreende padrões, pode revisar código crítico
- 🟢 Pode trabalhar com arquitetura mais complexa
- 🟢 Aprecia discussões sobre trade-offs e best practices

---

## 📋 Diretrizes Técnicas

### Ao Escrever Código
1. **Qualidade primeiro** - código limpo, bem estruturado e escalável
2. **TypeScript** - use como padrão em novos projetos (já que você é avançado)
3. **Padrões** - aplique design patterns apropriados sem overengineering
4. **Comentários** - apenas em lógica complexa ou decisões não-óbvias
5. **Testes** - considere test cases se o projeto for crítico

### Ao Arquitetar Soluções
- Proponha alternativas quando houver múltiplas abordagens válidas
- Mencione trade-offs (performance vs. manutenibilidade, etc)
- Considere escalabilidade desde o início
- Levante bandeiras vermelhas: segurança, rate limiting, caching

### Ao Revisar/Debugar
- Seja direto com problemas encontrados
- Sugira refatorações se virem necessárias
- Explique o "por que" de qualquer mudança proposta

---

## 🛠️ Stack Preferências (Customize Conforme Necessário)

### Frontend
- [ ] React (com hooks)
- [ ] Next.js
- [ ] TypeScript
- [ ] Tailwind CSS
- [ ] Vite (bundler)
- [ ] Outro: ____________

### Backend
- [ ] Node.js/Express
- [ ] TypeScript
- [ ] REST APIs
- [ ] GraphQL
- [ ] PostgreSQL
- [ ] MongoDB
- [ ] Outro: ____________

### Ferramentas & Ambiente
- [ ] Docker
- [ ] Git/GitHub
- [ ] ESLint + Prettier
- [ ] Jest/Vitest (testes)
- [ ] Postman/Insomnia (API testing)
- [ ] Outro: ____________

---

## 🚀 Fluxo de Trabalho Esperado

### Para Novos Projetos
1. **Briefing** - descreva requisitos, constraints, timeline
2. **Arquitetura** - eu proponho estrutura, você valida
3. **Desenvolvimento** - entregamos em chunks funcionais
4. **Review** - você revisa, sugere melhorias
5. **Deploy** - orientações de publicação se necessário

### Para Bugs/Melhorias
1. **Contexto** - código relevante + erro/comportamento esperado
2. **Investigação** - eu analiso e proponho fix
3. **Validação** - você testa a solução
4. **Integração** - incorpora no projeto

### Para Refatorações
1. **Identifique** - parte que quer melhorar
2. **Analiso** - problemas atuais + proposta
3. **Alternativas** - se houver trade-offs significativos
4. **Execute** - implemento a solução

---

## 🏗️ Arquitetura & Design de Sistema

### Princípios Arquiteturais
- **Single Responsibility Principle (SRP)** - cada componente/serviço tem uma responsabilidade
- **Separation of Concerns** - frontend, backend, database bem isolados
- **DRY (Don't Repeat Yourself)** - código reutilizável, não duplicado
- **KISS (Keep It Simple, Stupid)** - evite overengineering desnecessário
- **YAGNI (You Aren't Gonna Need It)** - não implemente features "para o futuro"

### Padrões Arquiteturais

#### Aplicações Web (Frontend)
- **Component-Based Architecture** - componentes reutilizáveis e isolados
- **State Management** - Redux, Zustand, Context API (conforme escala)
- **Custom Hooks** - lógica compartilhada entre componentes
- **Page/Container Pattern** - separar páginas de componentes reutilizáveis

#### Backend APIs
- **Layered Architecture** (Recomendado para seu caso)
  ```
  Routes → Controllers → Services → Repository → Database
  ```
- **Domain-Driven Design (DDD)** - se o domínio for complexo
- **Microservices** - apenas se escala/múltiplos times justificar
- **API Gateway Pattern** - para múltiplos serviços

#### Comunicação
- **REST APIs** - padrão para você? Use HTTP verbs corretamente
- **Webhooks** - para eventos assíncronos
- **Message Queues** (RabbitMQ, Redis) - processamento em background
- **GraphQL** - se houver queries complexas/múltiplos clients

### Escalabilidade

#### Frontend
- [ ] Code splitting (lazy loading de rotas/componentes)
- [ ] Caching strategy (HTTP cache headers, service workers)
- [ ] CDN para assets estáticos
- [ ] Monitore bundle size (webpack-bundle-analyzer)
- [ ] Performance metrics (Core Web Vitals)

#### Backend
- [ ] Database indexing estratégico (não indexe tudo)
- [ ] Query optimization (N+1 problems, select específico)
- [ ] Connection pooling (não abra nova conexão por request)
- [ ] Caching (Redis para dados frequentes)
- [ ] Rate limiting (proteção contra abuse)
- [ ] Horizontal scaling (load balancer, múltiplas instâncias)
- [ ] Logging & monitoring (não guarde tudo, seja seletivo)

### Decisões Arquiteturais (ADR - Architecture Decision Record)

Quando propuser arquitetura, documentarei assim:
```markdown
## ADR-001: [Título da Decisão]

### Contexto
Por que essa decisão é necessária?

### Opções Consideradas
1. Opção A - Pro: X, Con: Y
2. Opção B - Pro: X, Con: Y

### Decisão
Escolhemos a Opção B porque...

### Consequências
- Implicações positivas
- Tradeoffs aceitos
- Riscos residuais
```

### Padrões de Comunicação Backend

#### Request/Response Pattern
```javascript
// ✅ BOM - resposta estruturada
{
  success: true,
  data: { /* resultado */ },
  meta: { timestamp: "...", version: "..." }
}

// ❌ RUIM - estrutura inconsistente
{
  result: true,
  content: { /* resultado */ }
}
```

#### Error Handling
```javascript
// ✅ BOM - código HTTP apropriado + estrutura consistente
{
  success: false,
  error: {
    code: "VALIDATION_ERROR",
    message: "Email é obrigatório",
    field: "email"
  }
}

// ❌ RUIM - genérico demais
{
  error: "Erro no servidor"
}
```

### Versionamento de API
- [ ] URL versioning `/v1/`, `/v2/` (explícito)
- [ ] Header versioning `Accept: application/vnd.myapp.v2+json` (limpo)
- [ ] Deprecation warnings - avise clientes antes de remover

### Database Design
- **Normalization** - reduzir redundância
- **Relações** - PKs, FKs bem definidas
- **Constraints** - NOT NULL, UNIQUE onde apropriado
- **Migrations** - versionadas, reversíveis, testadasantes de deploy
- **Backup strategy** - frequência, retenção, teste de restore

### Observabilidade (Logging, Monitoring, Tracing)

#### Logs
- **Estruturados** - JSON, fácil de parsear
- **Níveis** - ERROR, WARN, INFO, DEBUG (não log tudo como INFO)
- **Contexto** - request ID, user ID, timestamp
- **Rotação** - não deixe logs crescerem indefinidamente

#### Métricas
- Latência (p50, p95, p99)
- Taxa de erro (5xx, validação)
- Throughput (requests/segundo)
- Resource usage (CPU, memória, conexões DB)

#### Alertas
- Defina thresholds sensatos (não triggere falsos positivos)
- Escalação clara (quem recebe, quando, como responder)
- Post-mortem: capture learnings de incidents

---

## 🔒 Cybersegurança

### Classificação de Dados

Antes de implementar qualquer feature, classifique os dados:

- **Público** - pode estar disponível para qualquer pessoa (preços, blog posts)
- **Interno** - apenas para funcionários (roadmap, salários)
- **Confidencial** - clientes/usuários específicos (orders, preferências)
- **Sensível** - precisa criptografia e audit (passwords, SSN, payment info)
- **PII (Personally Identifiable Information)** - nome, email, IP, endereço

### Autenticação

#### Passwords
- [ ] Salted + hashed com bcrypt/argon2 (NUNCA plain text)
- [ ] Mínimo 12 caracteres (enforce no frontend + backend)
- [ ] Rate limit login attempts (brute force protection)
- [ ] Logout deve invalidar sessões/tokens
- [ ] "Esqueci senha" - link com validade curta (1 hora)

#### Sessions
- [ ] Geradas server-side (não confie em claims do client)
- [ ] HTTPOnly + Secure cookies (HTTPS only, não acessível por JS)
- [ ] SameSite=Strict/Lax (CSRF protection)
- [ ] TTL apropriado (não eterno, ex: 1 dia)
- [ ] Rotação de session ID pós-login

#### Tokens (JWT, OAuth)
- [ ] Assinados (verificar assinatura sempre)
- [ ] Expiração curta (15-60 min, refresh token separado)
- [ ] Scope limitado (não incluir dados sensíveis)
- [ ] Revogação possível (blacklist, redis)
- [ ] Armazenar só em memória ou HTTPOnly cookies (nunca localStorage para sensitive)

#### Multi-Factor Authentication (MFA)
- [ ] Implemente se tiver dados sensíveis
- [ ] Suporte TOTP (Google Authenticator, Authy)
- [ ] Backup codes para recovery
- [ ] Rate limit MFA attempts também

### Autorização (Access Control)

#### Princípios
- **Least Privilege** - usuário tem permissão MÍNIMA necessária
- **Default Deny** - nega tudo, abre seletivamente
- **Role-Based Access Control (RBAC)** - user → role → permissions
- **Attribute-Based Access Control (ABAC)** - se lógica for muito complexa

#### Implementação
```javascript
// ✅ BOM - middleware verifica permissão
router.delete('/posts/:id', 
  requireAuth,           // usuário logado?
  checkOwnership,        // é o dono do post?
  deletePost             // execute a ação
);

// ❌ RUIM - sem validação
router.delete('/posts/:id', deletePost);
```

#### Auditoria
- [ ] Log quem faz quê (DELETE, UPDATE, CREATE)
- [ ] Timestamp + user ID + ação + dados antigos vs novos
- [ ] Retenção por lei (LGPD: mínimo 1 ano em geral)
- [ ] Immutable audit logs (não podem ser alterados)

### Proteção de Dados em Trânsito

#### HTTPS/TLS
- [ ] **Sempre ative HTTPS** (nunca HTTP em produção)
- [ ] Certificado válido (Let's Encrypt grátis)
- [ ] TLS 1.2+ (desabilite versões antigas)
- [ ] Forward Secrecy habilitado (Diffie-Hellman)
- [ ] HSTS header - force HTTPS em browsers

#### Headers de Segurança
```javascript
// Adicione estes headers em toda resposta:
app.use((req, res, next) => {
  res.set({
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' trusted.com",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
  });
  next();
});
```

### Proteção de Dados em Repouso

#### Criptografia
- [ ] Senhas - bcrypt/argon2 (salted, hashed)
- [ ] Tokens/Secrets - em `.env`, nunca em git
- [ ] Dados sensíveis - criptografia em nível de coluna (se GDPR/LGPD)
- [ ] Backups - criptografados também
- [ ] Chaves - rotação periódica (sem downtime)

#### Key Management
- [ ] Senhas de DB em environment variables
- [ ] API keys em vault (Doppler, HashiCorp Vault)
- [ ] Nenhum secret em git (use `.env.example` sem valores)
- [ ] Rotação automática se possível
- [ ] Rastreio de acesso (quem acessou que secret)

### Injeção de Dados

#### SQL Injection
```javascript
// ❌ VULNERÁVEL
db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);

// ✅ SEGURO - prepared statement
db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
```

#### NoSQL Injection
```javascript
// ❌ VULNERÁVEL
User.find({ email: req.body.email });
// Se email = { $ne: null }, retorna TODOS os usuários

// ✅ SEGURO - validar e sanitizar
const email = String(req.body.email).trim();
User.find({ email });
```

#### Command Injection
```javascript
// ❌ VULNERÁVEL
exec(`rm -rf ${folderName}`); // folderName pode ser "; rm -rf /"

// ✅ SEGURO - use child_process sem shell
execFile('rm', ['-rf', folderName]);
```

#### XSS (Cross-Site Scripting)
```javascript
// ❌ VULNERÁVEL - renderizar HTML direto
<div>{userInput}</div>

// ✅ SEGURO - React escapa por padrão
<div>{userInput}</div>

// Ou sanitize se precisar de HTML
import DOMPurify from 'dompurify';
<div>{DOMPurify.sanitize(htmlContent)}</div>
```

### CORS (Cross-Origin Resource Sharing)

```javascript
// ❌ ABERTO DEMAIS
app.use(cors()); // qualquer origem pode acessar

// ✅ RESTRITIVO
app.use(cors({
  origin: ['https://seudominio.com', 'https://app.seudominio.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

### CSRF (Cross-Site Request Forgery)

```javascript
// ✅ Use tokens CSRF em formulários
<form method="POST">
  <input type="hidden" name="_csrf" value={token} />
  <!-- campos do form -->
</form>

// Backend valida:
app.post('/action', csrfProtection, (req, res) => {
  // processa se token for válido
});
```

### Rate Limiting & DDoS

```javascript
// ✅ Limite requests por IP/usuário
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // max 100 requests
  message: 'Muitas requisições, tente depois'
});

app.use('/api/', limiter);

// Limites mais estritos para login
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // apenas 5 tentativas
  skipSuccessfulRequests: true
});

app.post('/login', loginLimiter, loginHandler);
```

### Validação de Input

```javascript
// ✅ BOM - validar TUDO no backend
import { body, validationResult } from 'express-validator';

app.post('/register',
  body('email').isEmail(),
  body('password').isLength({ min: 12 }),
  body('name').trim().notEmpty(),
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    // processa
  }
);

// ❌ RUIM - confiar no frontend
if (req.body.email.includes('@')) {
  // processa
}
```

### Uploaded Files

```javascript
// ✅ SEGURO
- [ ] Validar tipo de arquivo (whitelist, não blacklist)
- [ ] Validar tamanho (limite máximo)
- [ ] Salvar fora da raiz web (não servir direto)
- [ ] Renomear arquivo (não use nome do usuário)
- [ ] Scan de malware (ClamAV, VirusTotal)
- [ ] Servir com headers apropriados (Content-Disposition: attachment)

// ❌ NÃO FAÇA
- Servir arquivo direto de /public
- Permitir qualquer extensão
- Confiar na extensão do usuário
```

### Logging de Segurança

```javascript
// ✅ Log eventos críticos
- [ ] Failed login attempts (com IP, user agent)
- [ ] Permission changes
- [ ] Sensitive data access
- [ ] Admin actions
- [ ] API key usage
- [ ] Unusual patterns (muitas requests de um IP)

// ❌ NÃO LOG
- Passwords (even hashed, é desnecessário)
- Full request bodies (pode conter dados sensíveis)
- Session tokens (risco de exposição)
```

### Dependências & Vulnerabilidades

```bash
# ✅ Verifique vulnerabilidades regularmente
npm audit
npm audit fix

# Mantenha packages atualizados
npm update

# Use ferramentas para CI/CD
# - npm audit no pipeline
# - Snyk para scanning contínuo
# - OWASP Dependency-Check
```

### Políticas de Segurança

#### .env (nunca commite!)
```
DATABASE_URL=postgresql://user:pass@localhost/db
JWT_SECRET=seu_secret_super_seguro
API_KEY=xyz123
```

#### .gitignore
```
.env
.env.local
*.key
*.pem
node_modules/
```

#### Secrets Rotation
- [ ] Planeje rotação periódica (90 dias, anualmente conforme sensibilidade)
- [ ] Versione segredos (v1, v2)
- [ ] Período de graça (aceite antigos e novos)
- [ ] Teste antes de remover antigos

### Incidente & Resposta

```markdown
## Plano de Resposta a Incidentes de Segurança

### Detecção
- Alertas automáticos (logs anormais, falhas de autenticação)
- Relatórios de usuários
- Scans de segurança

### Resposta Imediata
1. Isole o sistema (pare a sangria)
2. Preserve evidências (logs, snapshots)
3. Notifique stakeholders
4. Ative plano de continuidade

### Investigação
- Determine scope (quais dados foram afetados?)
- Timeline (quando começou?)
- Root cause (como entrou?)

### Notificação (LGPD)
- Usuarios afetados (ASAP, máximo 72h)
- Autoridades (se necessário)
- Imprensa (se público)

### Remediação
- Patch vulnerabilidade
- Reset de credentials
- Monitor por atividade suspeita

### Post-Mortem
- Documentar o que aconteceu
- Lições aprendidas
- Melhorias implementadas
```

### Compliance & Regulações

#### LGPD (Lei Geral de Proteção de Dados - Brasil)
- [ ] Consentimento explícito para coletar dados
- [ ] Direito de acesso aos dados (API endpoint)
- [ ] Direito de exclusão (delete da conta)
- [ ] Criptografia de dados sensíveis
- [ ] Notificação em caso de breach (72h)
- [ ] Data Processing Agreement com fornecedores

#### GDPR (EU)
- [ ] LGPD + Consentimento pré-carregamento (cookies)
- [ ] Privacy by Design
- [ ] Data Protection Officer designado
- [ ] Right to be forgotten (completo)

### Checklist Pré-Deploy

- [ ] HTTPS ativado
- [ ] Senhas hasheadas (bcrypt+)
- [ ] Rate limiting ativo
- [ ] Validação de input no backend
- [ ] CORS restritivo
- [ ] Audit logs configurados
- [ ] Secrets em .env (não no código)
- [ ] Dependencies auditadas
- [ ] Security headers presentes
- [ ] Session/Token TTL apropriado
- [ ] Plano de incidente documentado

---

## 💡 Quando Me Envolver

### ✅ Peça Ajuda Com
- Arquitetura e design de sistema
- Troubleshooting e debugging
- Code review e refatoração
- Performance optimization
- Segurança (CORS, autenticação, validação, etc)
- SQL queries complexas
- API design (RESTful patterns, versioning, etc)
- Testes (estratégia e implementação)

### ❌ Não Pergunte Sem Contexto
- "Como aprendo React?" (conceitos básicos - você já sabe)
- Copiar/colar código gigante sem explicar o problema
- Coisas que um search rápido resolveria

---

## 🔐 Boas Práticas & Segurança

### Sempre Que Relevante
- [ ] Validar inputs (frontend + backend)
- [ ] HTTPS + CORS configurado corretamente
- [ ] Secrets em `.env` (nunca em git)
- [ ] Rate limiting em APIs públicas
- [ ] SQL injection prevention (prepared statements)
- [ ] XSS protection (sanitize user input)
- [ ] CSRF tokens para formulários
- [ ] Autenticação/Autorização clara

### Antes de Deploy
- Revisar variáveis de ambiente
- Verificar permissões de acesso
- Testar em staging
- Backup/rollback strategy

---

## 📊 Padrões & Convenções Preferidos

### Nomeação
- **camelCase** para variáveis/funções (JS/TS)
- **PascalCase** para componentes React
- **SCREAMING_SNAKE_CASE** para constantes
- **kebab-case** para URLs/rotas

### Estrutura de Pastas (Backend)
```
src/
├── routes/
├── controllers/
├── services/
├── models/
├── middleware/
├── utils/
├── config/
└── types/
```

### Estrutura de Pastas (Frontend React)
```
src/
├── components/
├── pages/
├── hooks/
├── services/
├── utils/
├── types/
├── styles/
└── assets/
```

---

## 🔄 Feedback & Iteração

### Como Você Pode Me Guiar Melhor
- **Teste o código** e me avise se quebrou algo
- **Pergunte "por quê?"** se algo não ficar claro
- **Revise** propostas e sugira mudanças
- **Atualize este arquivo** conforme seus padrões evoluem

### Sinais de Que Algo Está Errado
- Código muito genérico ou overengineered
- Falta de tipos/tipos muito soltos em TS
- Sem tratamento de erros
- Performance ignorada
- Sem separação de concerns

---

## 📝 Checklist Antes de Compartilhar Código

- [ ] Código está funcionando (ou expliquei por que não)
- [ ] Segui convenções do projeto/linguagem
- [ ] Considerei edge cases
- [ ] TypeScript types estão corretos
- [ ] Não há `any` desnecessários
- [ ] Tratamento de erros incluso
- [ ] Comentários só onde necessário
- [ ] Performance razoável (sem premature optimization)

---

## 🎓 Recursos & Documentação

### Seu Contexto Pessoal
- **Localização:** São Paulo, BR (timezone: -3)
- **Experiência:** Avançado em full-stack
- **Estilo:** Balanceado - quer aprender, não copiar/colar
- **Linguagem Preferida:** Português (com termos técnicos em inglês)

### Links Úteis (Customize Conforme Necessário)
- [ ] Documentação do projeto principal
- [ ] Wiki interno
- [ ] Design system
- [ ] API docs
- [ ] Deploy guide
- [ ] Outro: ____________

---

## 🚨 Avisos & Limitações

### Coisas Que Não Posso Fazer
- Gerar código sem entender requisitos
- Debugar sem informações de erro
- Garantir segurança em código incompleto
- Fazer commits ou fazer deploy por você
- Acessar bases de dados reais (use staging)

### Coisas Que Você Deve Fazer
- Validar código em ambiente local antes de mergear
- Revisar segurança com seu time
- Testar em staging antes de produção
- Manter este arquivo atualizado
- Comunicar mudanças de tech stack

---

## ✨ Final Notes

Este arquivo é **vivo** - atualize conforme seu contexto mudar:
- Novos padrões adotados
- Tech stack evoluindo
- Preferências pessoais ajustadas
- Novos projetos com constraints diferentes

**Última atualização:** 29 de Abril de 2026

---

### Template para Pedir Ajuda Eficientemente

```markdown
## Projeto: [Nome]

### O que preciso fazer?
[Descrição clara do objetivo]

### Contexto
- **Linguagem/Framework:** 
- **Arquivo relevante:** 
- **Erro/Comportamento esperado:** 

### O que já tentei?
[Se aplicável]

### Constraint/Preferência especial?
[Se houver]
```

**Pronto para codar! 🚀**