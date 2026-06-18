#!/usr/bin/env python3
"""
Idea Processor - Processa entradas brutas (voz/texto) em threads estruturadas.
Parte da Hermes Incubadora de Ideias.
"""

import re
import json
import asyncio
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IdeaSource(Enum):
    VOICE = "voice"
    TEXT = "text"
    REACTION = "reaction"
    SLASH_COMMAND = "slash_command"


class IdeaType(Enum):
    FEATURE = "feature"
    BUG = "bug"
    TECH_DEBT = "tech-debt"
    RESEARCH = "pesquisa"
    PROCESS = "processo"
    INFRA = "infra"


class Priority(Enum):
    P1_URGENTE = "P1-urgente"
    P2_ALTA = "P2-alta"
    P3_NORMAL = "P3-normal"
    P4_BAIXA = "P4-baixa"
    P5_BACKLOG = "P5-backlog"


class Effort(Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    UNKNOWN = "desconhecido"


class Domain(Enum):
    CAREER = "career"
    PIM = "pim"
    ROUTER = "router"
    INFRA = "infra"
    HERMES = "hermes"
    GERAL = "geral"


@dataclass
class RawIdea:
    """Ideia bruta capturada."""
    source: IdeaSource
    content: str
    author_id: str
    author_name: str
    channel_id: str
    message_id: str
    timestamp: str
    attachments: List[dict] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []


@dataclass
class StructuredIdea:
    """Ideia estruturada pronta para thread."""
    title: str
    content: str
    tipo: IdeaType
    prioridade: Priority
    esforco: Effort
    dominio: Domain
    status: str = "capturada"
    contexto: str = ""
    hipotese_valor: str = ""
    criterios_sucesso: List[str] = None
    riscos: List[str] = None
    dependencias: List[str] = None
    estimativa_mvp: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.criterios_sucesso is None:
            self.criterios_sucesso = []
        if self.riscos is None:
            self.riscos = []
        if self.dependencias is None:
            self.dependencias = []
        if self.metadata is None:
            self.metadata = {}


# ============== TEMPLATES ==============

THREAD_TEMPLATE = """## 💡 Ideia: {title}

### Contexto
{contexto}

### Hipótese de Valor
{hipotese_valor}

### Critérios de Sucesso
{criterios}

### Riscos Conhecidos
{riscos}

### Dependências
{dependencias}

### Estimativa Rápida
- **Esforço:** {esforco}
- **Complexidade técnica:** {complexidade}
- **Tempo para MVP:** {mvp}

---

### 💬 Discussão
<!---thread-messages-->

### ✅ Decisão
- **Status:** {status}
- **Decisor:** @{author}
- **Data:** {date}
- **Próximo passo:** {proximo_passo}
"""


def format_criteria(criteria: List[str]) -> str:
    if not criteria:
        return "- [ ] A definir durante debate"
    return "\n".join(f"- [ ] {c}" for c in criteria)


def format_risks(risks: List[str]) -> str:
    if not risks:
        return "- Nenhum risco identificado ainda"
    return "\n".join(f"- {r}" for r in risks)


def format_deps(deps: List[str]) -> str:
    if not deps:
        return "- Nenhuma dependência conhecida"
    return "\n".join(f"- {d}" for d in deps)


# ============== PROCESSADOR PRINCIPAL ==============

class IdeaProcessor:
    """Processa ideias brutas em threads estruturadas."""
    
    # Palavras-chave para classificação automática
    TYPE_KEYWORDS = {
        IdeaType.FEATURE: ["feature", "funcionalidade", "nova", "adicionar", "criar", "implementar", "precisamos de"],
        IdeaType.BUG: ["bug", "erro", "falha", "quebrado", "não funciona", "problema", "issue"],
        IdeaType.TECH_DEBT: ["refatorar", "refactor", "tech debt", "dívida técnica", "limpar", "melhorar código", "deprecated"],
        IdeaType.RESEARCH: ["pesquisar", "investigar", "spike", "poc", "proof of concept", "validar", "testar se"],
        IdeaType.PROCESS: ["processo", "workflow", "fluxo", "como fazemos", "padronizar", "automatizar"],
        IdeaType.INFRA: ["infra", "servidor", "deploy", "ci/cd", "docker", "kubernetes", "cloud", "vps"],
    }
    
    DOMAIN_KEYWORDS = {
        Domain.CAREER: ["career", "carreira", "cv", "currículo", "emprego", "vaga", "linkedin", "ats"],
        Domain.PIM: ["pim", "produto", "amazon", "tiny", "reval", "sku", "estoque", "marketplace"],
        Domain.ROUTER: ["router", "roteador", "llm", "modelo", "provider", "fallback", "api key"],
        Domain.INFRA: ["infra", "servidor", "vps", "caddy", "cloudflare", "dns", "ssl", "nginx"],
        Domain.HERMES: ["hermes", "agente", "gateway", "skill", "cron", "kanban", "workspace"],
    }
    
    PRIORITY_KEYWORDS = {
        Priority.P1_URGENTE: ["urgente", "crítico", "bloqueador", "produção caiu", "hotfix", "asap"],
        Priority.P2_ALTA: ["importante", "prioridade alta", "precisa rápido", "esta semana"],
        Priority.P3_NORMAL: ["normal", "quando der", "backlog", "futuro"],
        Priority.P4_BAIXA: ["baixa", "nice to have", "eventualmente", "um dia"],
        Priority.P5_BACKLOG: ["backlog", "estacionado", "depois", "talvez"],
    }
    
    EFFORT_KEYWORDS = {
        Effort.XS: ["minúsculo", "tiny", "5 min", "rápido", "trivial"],
        Effort.S: ["pequeno", "small", "horas", "meio dia", "simples"],
        Effort.M: ["médio", "medium", "dias", "alguns dias", "moderado"],
        Effort.L: ["grande", "large", "semana", "duas semanas", "complexo"],
        Effort.XL: ["enorme", "xl", "mês", "meses", "muito complexo", "projeto grande"],
    }
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client  # Opcional: para análise mais sofisticada
    
    def process_raw_idea(self, raw: RawIdea) -> StructuredIdea:
        """Processa ideia bruta em estrutura completa."""
        content = raw.content.strip()
        
        # Se veio de voice, fazer limpeza básica
        if raw.source == IdeaSource.VOICE:
            content = self._clean_voice_transcript(content)
        
        # Extrair título (primeira frase ou até 80 chars)
        title = self._extract_title(content)
        
        # Classificar automaticamente
        tipo = self._classify_type(content)
        prioridade = self._classify_priority(content)
        esforco = self._classify_effort(content)
        dominio = self._classify_domain(content)
        
        # Extrair seções se houver marcadores
        sections = self._extract_sections(content)
        
        # Construir ideia estruturada
        idea = StructuredIdea(
            title=title,
            content=self._build_thread_content(content, sections, raw),
            tipo=tipo,
            prioridade=prioridade,
            esforco=esforco,
            dominio=dominio,
            contexto=sections.get("contexto", content[:500]),
            hipotese_valor=sections.get("hipotese", ""),
            criterios_sucesso=sections.get("criterios", []),
            riscos=sections.get("riscos", []),
            dependencias=sections.get("dependencias", []),
            estimativa_mvp=sections.get("mvp", ""),
            metadata={
                "source": raw.source.value,
                "author_id": raw.author_id,
                "author_name": raw.author_name,
                "original_channel": raw.channel_id,
                "original_message": raw.message_id,
                "timestamp": raw.timestamp,
                "attachments_count": len(raw.attachments),
            },
        )
        
        return idea
    
    def _clean_voice_transcript(self, text: str) -> str:
        """Limpa transcrição de voz (remove filler words, repetições)."""
        # Remover filler words comuns em PT-BR
        fillers = [
            r"\b(eh|hum|tipo|né|então|aí|é|pois é|basicamente|praticamente)\b",
            r"\b(é tipo|é assim|vou falar|deixa eu ver)\b",
        ]
        for pattern in fillers:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        # Normalizar espaços
        text = re.sub(r"\s+", " ", text).strip()
        
        # Capitalizar primeiras letras de frases
        sentences = re.split(r"([.!?]+)", text)
        result = []
        for i, s in enumerate(sentences):
            if i % 2 == 0 and s.strip():
                result.append(s.strip().capitalize())
            else:
                result.append(s)
        return "".join(result)
    
    def _extract_title(self, content: str) -> str:
        """Extrai título da ideia."""
        # Primeira frase completa
        sentences = re.split(r"[.!?]+", content)
        first_sentence = sentences[0].strip() if sentences else content
        
        # Limitar a 80 chars
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."
        
        return first_sentence
    
    def _classify_type(self, content: str) -> IdeaType:
        content_lower = content.lower()
        scores = {}
        for itype, keywords in self.TYPE_KEYWORDS.items():
            scores[itype] = sum(1 for kw in keywords if kw in content_lower)
        return max(scores, key=scores.get) if max(scores.values()) > 0 else IdeaType.FEATURE
    
    def _classify_priority(self, content: str) -> Priority:
        content_lower = content.lower()
        scores = {}
        for prio, keywords in self.PRIORITY_KEYWORDS.items():
            scores[prio] = sum(2 if kw in content_lower else 0 for kw in keywords)
        return max(scores, key=scores.get) if max(scores.values()) > 0 else Priority.P3_NORMAL
    
    def _classify_effort(self, content: str) -> Effort:
        content_lower = content.lower()
        scores = {}
        for effort, keywords in self.EFFORT_KEYWORDS.items():
            scores[effort] = sum(1 for kw in keywords if kw in content_lower)
        return max(scores, key=scores.get) if max(scores.values()) > 0 else Effort.UNKNOWN
    
    def _classify_domain(self, content: str) -> Domain:
        content_lower = content.lower()
        scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            scores[domain] = sum(1 for kw in keywords if kw in content_lower)
        return max(scores, key=scores.get) if max(scores.values()) > 0 else Domain.GERAL
    
    def _extract_sections(self, content: str) -> Dict[str, Any]:
        """Extrai seções estruturadas se houver marcadores."""
        sections = {}
        
        patterns = {
            "contexto": r"(?:contexto|background|motivação)[:\n](.+?)(?:\n\n|\n\w+:|$)",
            "hipotese": r"(?:hipótese|hipotese|value prop|valor)[:\n](.+?)(?:\n\n|\n\w+:|$)",
            "criterios": r"(?:critéri?rios?|aceite|acceptance)[:\n](.+?)(?:\n\n|\n\w+:|$)",
            "riscos": r"(?:riscos?|risks?)[:\n](.+?)(?:\n\n|\n\w+:|$)",
            "dependencias": r"(?:dependênc?ias?|deps|dependencias)[:\n](.+?)(?:\n\n|\n\w+:|$)",
            "mvp": r"(?:mvp|tempo|estimativa|prazo)[:\n](.+?)(?:\n\n|\n\w+:|$)",
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                if key == "criterios":
                    # Split em lista por linhas ou bullets
                    sections[key] = [c.strip("- • ").strip() for c in value.split("\n") if c.strip()]
                else:
                    sections[key] = value
        
        return sections
    
    def _build_thread_content(self, original: str, sections: dict, raw: RawIdea) -> str:
        """Constrói conteúdo completo da thread."""
        return THREAD_TEMPLATE.format(
            title=self._extract_title(original),
            contexto=sections.get("contexto", original[:500]),
            hipotese_valor=sections.get("hipotese", "A ser definida durante debate"),
            criterios=format_criteria(sections.get("criterios", [])),
            riscos=format_risks(sections.get("riscos", [])),
            dependencias=format_deps(sections.get("dependencias", [])),
            esforco=self._classify_effort(original).value,
            complexidade=self._estimate_complexity(original),
            mvp=sections.get("mvp", "A definir"),
            status="capturada",
            author=raw.author_name,
            date=datetime.now().strftime("%Y-%m-%d"),
            proximo_passo="Aguardando triagem/debate",
        )
    
    def _estimate_complexity(self, content: str) -> str:
        """Estima complexidade técnica baseada em heurísticas."""
        content_lower = content.lower()
        complexity_indicators = [
            "arquitetura", "refator", "migração", "integração", "api", "banco de dados",
            "database", "schema", "auth", "autenticação", "segurança", "performance",
            "escalabilidade", "microserv", "queue", "fila", "event", "grpc", "graphql",
        ]
        count = sum(1 for ind in complexity_indicators if ind in content_lower)
        if count >= 3:
            return "Alta"
        elif count >= 1:
            return "Média"
        return "Baixa"
    
    # ============== SLASH COMMAND PARSER ==============
    
    SLASH_PATTERN = re.compile(
        r'/ideia\s+"([^"]+)"'
        r'(?:\s+--tipo\s+(\w+(?:-\w+)?))?'
        r'(?:\s+--prioridade\s+(\w+(?:-\w+)?))?'
        r'(?:\s+--dominio\s+(\w+(?:-\w+)?))?'
        r'(?:\s+--esforco\s+(\w+(?:-\w+)?))?'
    )
    
    def parse_slash_command(self, content: str) -> Optional[Dict[str, str]]:
        """Parse do comando /ideia "titulo" --tipo feature --prioridade P3 ..."""
        match = self.SLASH_PATTERN.search(content)
        if not match:
            return None
        
        title, tipo, prioridade, dominio, esforco = match.groups()
        return {
            "title": title,
            "tipo": tipo,
            "prioridade": prioridade,
            "dominio": dominio,
            "esforco": esforco,
        }
    
    def apply_slash_overrides(
        self,
        idea: StructuredIdea,
        overrides: Dict[str, str],
    ) -> StructuredIdea:
        """Aplica overrides do slash command."""
        if overrides.get("tipo"):
            try:
                idea.tipo = IdeaType(overrides["tipo"])
            except ValueError:
                pass
        if overrides.get("prioridade"):
            try:
                idea.prioridade = Priority(overrides["prioridade"])
            except ValueError:
                pass
        if overrides.get("dominio"):
            try:
                idea.dominio = Domain(overrides["dominio"])
            except ValueError:
                pass
        if overrides.get("esforco"):
            try:
                idea.esforco = Effort(overrides["esforco"])
            except ValueError:
                pass
        return idea


# ============== HELPER FUNCTIONS ==============

def create_raw_idea_from_discord_message(message: dict) -> RawIdea:
    """Cria RawIdea a partir de mensagem do Discord (webhook/gateway)."""
    return RawIdea(
        source=IdeaSource.TEXT,
        content=message.get("content", ""),
        author_id=message.get("author", {}).get("id", ""),
        author_name=message.get("author", {}).get("username", "unknown"),
        channel_id=message.get("channel_id", ""),
        message_id=message.get("id", ""),
        timestamp=message.get("timestamp", datetime.now().isoformat()),
        attachments=message.get("attachments", []),
    )


def create_raw_idea_from_voice(
    transcript: str,
    author_id: str,
    author_name: str,
    channel_id: str,
    message_id: str,
) -> RawIdea:
    """Cria RawIdea a partir de transcrição de voz."""
    return RawIdea(
        source=IdeaSource.VOICE,
        content=transcript,
        author_id=author_id,
        author_name=author_name,
        channel_id=channel_id,
        message_id=message_id,
        timestamp=datetime.now().isoformat(),
    )


def create_raw_idea_from_reaction(
    message: dict,
    emoji: str,
    reactor_id: str,
    reactor_name: str,
) -> RawIdea:
    """Cria RawIdea a partir de reação em mensagem."""
    return RawIdea(
        source=IdeaSource.REACTION,
        content=f"[Reação {emoji}] {message.get('content', '')}",
        author_id=reactor_id,
        author_name=reactor_name,
        channel_id=message.get("channel_id", ""),
        message_id=message.get("id", ""),
        timestamp=datetime.now().isoformat(),
    )


if __name__ == "__main__":
    # Teste rápido
    processor = IdeaProcessor()
    
    # Teste 1: Texto livre
    raw1 = RawIdea(
        source=IdeaSource.TEXT,
        content="Precisamos adicionar autenticação OAuth no Career Hub. O login atual só usa email/senha. Isso vai permitir login com Google/GitHub. Esforço médio, prioridade alta.",
        author_id="123",
        author_name="Carlos",
        channel_id="456",
        message_id="789",
        timestamp="2026-06-17T10:00:00Z",
    )
    
    idea1 = processor.process_raw_idea(raw1)
    print("=== IDEIA 1 (Texto) ===")
    print(f"Título: {idea1.title}")
    print(f"Tipo: {idea1.tipo.value}")
    print(f"Prioridade: {idea1.prioridade.value}")
    print(f"Esforço: {idea1.esforco.value}")
    print(f"Domínio: {idea1.dominio.value}")
    print(f"\nConteúdo da thread:\n{idea1.content[:500]}...")
    
    # Teste 2: Slash command
    slash_content = '/ideia "OAuth no Career Hub" --tipo feature --prioridade P2-alta --dominio career --esforco M'
    overrides = processor.parse_slash_command(slash_content)
    print(f"\n=== SLASH PARSE ===")
    print(overrides)
    
    # Teste 3: Voice transcript
    raw3 = RawIdea(
        source=IdeaSource.VOICE,
        content="Ah, tipo, eu tava pensando... hum... a gente podia fazer um webhook pro Tiny avisar quando o estoque muda, né? Isso ia evitar a gente ter que ficar consultando a API toda hora. Basicamente é um webhook de estoque.",
        author_id="123",
        author_name="Carlos",
        channel_id="456",
        message_id="999",
        timestamp="2026-06-17T11:00:00Z",
    )
    
    idea3 = processor.process_raw_idea(raw3)
    print("\n=== IDEIA 3 (Voice) ===")
    print(f"Título: {idea3.title}")
    print(f"Tipo: {idea3.tipo.value}")
    print(f"Prioridade: {idea3.prioridade.value}")
    print(f"Esforço: {idea3.esforco.value}")
    print(f"Domínio: {idea3.dominio.value}")