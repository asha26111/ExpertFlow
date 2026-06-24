"""
RAG + Mixture of Experts (MoE) Service
Covers ALL academic subjects with deep specialized experts and knowledge bases.
Uses Gemini API for cloud LLM inference — free tier at aistudio.google.com
"""
import json
from google import genai
from google.genai import types as genai_types
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# ── Mixture-of-Experts: 14 specialized domains ──────────────────────────────
EXPERTS = {
    "mathematics": {
        "name": "Math Expert", "icon": "📐",
        "keywords": [
            "math","algebra","calculus","geometry","equation","integral","derivative",
            "matrix","vector","probability","statistics","trigonometry","logarithm",
            "polynomial","theorem","proof","limit","series","sequence","function",
            "graph","coordinate","set","number","arithmetic","fraction","factor",
            "prime","complex","differential","gradient","eigenvalue","determinant",
            "binomial","permutation","combination","quadratic","linear","parabola",
            "hyperbola","ellipse","sine","cosine","tangent","radian","median","mean",
            "variance","standard deviation","regression","hypothesis","modulus"
        ],
        "system_prompt": """You are a Mathematics tutor. Answer the math question thoroughly.
- Answer the exact question, nothing else
- Show step-by-step working for calculations
- Use clear notation
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "physics": {
        "name": "Physics Expert", "icon": "⚛️",
        "keywords": [
            "physics","force","energy","momentum","gravity","wave","quantum","relativity",
            "thermodynamics","electricity","magnetism","optics","velocity","acceleration",
            "mass","charge","current","voltage","resistance","field","pressure","density",
            "frequency","wavelength","photon","electron","nucleus","orbital","circuit",
            "entropy","capacitor","inductor","refraction","diffraction","interference",
            "torque","friction","tension","normal","work","power","collision","projectile",
            "circular motion","simple harmonic","pendulum","doppler","snell","faraday",
            "lenz","coulomb","gauss","ampere","solenoid","radioactivity"
        ],
        "system_prompt": """You are a Physics tutor. Answer the physics question thoroughly.
- Answer the exact question, nothing else
- State the formula, substitute values, solve
- Always include units
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "computer_science": {
        "name": "CS Expert", "icon": "💻",
        "keywords": [
            "code","program","algorithm","data structure","python","java","javascript",
            "database","ai","machine learning","neural","complexity","bug","debug",
            "function","class","object","array","list","loop","recursion","stack",
            "queue","tree","heap","graph","hash","sort","search","pointer","memory",
            "compiler","interpreter","operating system","network","http","api",
            "rest","sql","nosql","mongodb","postgresql","react","node","django","flask",
            "fastapi","docker","kubernetes","git","linux","bash","shell","regex",
            "binary","bit","byte","cpu","thread","process","async","concurrency",
            "oop","functional","design pattern","solid","refactor","test","unit test","sentence transformer","transformer","embedding","transformer model","bert","llm","large language",
            "typescript","rust","c++","golang","kotlin","swift","html","css"
        ],
        "system_prompt": """You are a programming tutor. Answer the coding question thoroughly.
- Write clean, working code with brief comments
- Explain only what was asked
- Give time/space complexity only if relevant to the question
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "chemistry": {
        "name": "Chemistry Expert", "icon": "🧪",
        "keywords": [
            "chemistry","chemical","reaction","molecule","atom","bond","organic",
            "periodic","element","compound","acid","base","salt","buffer","solution",
            "molarity","mole","avogadro","equilibrium","kinetics","thermochemistry",
            "enthalpy","entropy","gibbs","electrochemistry","oxidation","reduction",
            "redox","electrolysis","polymer","isomer","alkane","alkene","aromatic",
            "benzene","aldehyde","ketone","ester","amine","amino acid","titration",
            "ph","indicator","catalyst","activation energy","arrhenius","colligative",
            "ideal gas","van der waals","ionization","electron configuration","orbital"
        ],
        "system_prompt": """You are a Chemistry tutor. Answer the chemistry question thoroughly.
- Answer exactly what was asked
- Show equations and calculations clearly
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "biology": {
        "name": "Biology Expert", "icon": "🧬",
        "keywords": [
            "biology","cell","gene","dna","rna","protein","evolution","ecology",
            "anatomy","physiology","organism","species","mitosis","meiosis","photosynthesis",
            "respiration","enzyme","hormone","neuron","synapse","immune","antibody",
            "virus","bacteria","fungi","plant","animal","ecosystem","food chain",
            "natural selection","mutation","chromosome","allele","dominant","recessive",
            "mendel","darwin","krebs","atp","mitochondria","chloroplast","ribosome",
            "membrane","osmosis","diffusion","active transport","nervous system",
            "cardiovascular","respiratory","digestive","endocrine","reproductive"
        ],
        "system_prompt": """You are a Biology tutor. Answer the biology question thoroughly.
- Answer exactly what was asked, clearly and concisely
- Use correct terms but explain them simply
- CRITICAL: If retrieved context is provided, it contains verified facts — USE IT as your primary source of truth
- For human anatomy facts (bones, organs, muscles etc.), always rely on the retrieved context
- NEVER guess or estimate numbers — if the retrieved context says 206 bones, answer 206 bones"""
    },

    "history": {
        "name": "History Expert", "icon": "📜",
        "keywords": [
            "history","war","revolution","empire","dynasty","civilization","century",
            "ancient","medieval","modern","colonial","independence","treaty","battle",
            "king","queen","emperor","president","parliament","democracy","monarchy",
            "world war","cold war","renaissance","reformation","enlightenment","industrial",
            "egypt","rome","greece","india","china","british","french","american",
            "russian","ottoman","mughal","maurya","gupta","byzantine","viking","crusade",
            "partition","nationalism","imperialism","communism","fascism","holocaust",
            "civil rights","decolonization","1857","1947","1776","1789","1914","1939"
        ],
        "system_prompt": """You are a History tutor. Answer the history question thoroughly.
- Answer exactly what was asked with key facts, dates, people
- Be concise and focused
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "geography": {
        "name": "Geography Expert", "icon": "🌍",
        "keywords": [
            "geography","map","continent","country","ocean","river","mountain","climate",
            "weather","biome","ecosystem","plate tectonics","earthquake","volcano","erosion",
            "deposition","population","urbanization","migration","development","gdp","hdi",
            "poverty","inequality","sustainability","resource","energy","trade","globalization",
            "latitude","longitude","altitude","rainfall","temperature","humidity","monsoon",
            "drought","flood","tsunami","hurricane","tornado","glacier","permafrost",
            "rainforest","savanna","desert","tundra","coral reef","delta","estuary"
        ],
        "system_prompt": """You are a Geography tutor. Answer the geography question thoroughly.
- Answer exactly what was asked
- Use specific examples where helpful
- Do NOT mix in unrelated geography concepts
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "economics": {
        "name": "Economics Expert", "icon": "📊",
        "keywords": [
            "economics","supply","demand","market","price","inflation","gdp","trade",
            "fiscal","monetary","policy","interest rate","unemployment","recession",
            "growth","elasticity","cost","revenue","profit","equilibrium","monopoly",
            "oligopoly","competition","externality","public good","tax","subsidy",
            "budget","deficit","surplus","exchange rate","balance of payments",
            "comparative advantage","protectionism","tariff","quota","microeconomics",
            "macroeconomics","keynesian","classical","aggregate demand","aggregate supply",
            "multiplier","accelerator","investment","consumption","savings","stock market"
        ],
        "system_prompt": """You are an Economics tutor. Answer the economics question thoroughly.
- Answer exactly what was asked
- Use simple examples to illustrate
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "literature_english": {
        "name": "Literature & English Expert", "icon": "📚",
        "keywords": [
            "literature","novel","poem","poetry","essay","grammar","writing","shakespeare",
            "metaphor","simile","imagery","tone","voice","narrative","prose","fiction",
            "theme","character","plot","setting","conflict","symbolism","alliteration",
            "irony","foreshadowing","protagonist","antagonist","stanza","rhyme","meter",
            "sonnet","tragedy","comedy","dystopia","genre","author","context","analysis",
            "paragraph","sentence","vocabulary","synonym","antonym","spelling","punctuation",
            "verb","noun","adjective","adverb","preposition","clause","tense","passive",
            "active","citation","bibliography","thesis","argument","rhetoric","persuasion"
        ],
        "system_prompt": """You are an English and Literature tutor. Answer ONLY the specific question asked.
- Answer exactly what was asked
- For grammar: give the rule and a clear example
- For literature: focus on the specific text/device/topic asked
- Do NOT expand into unrelated language or literary topics
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "psychology": {
        "name": "Psychology Expert", "icon": "🧠",
        "keywords": [
            "psychology","behavior","mind","mental","cognition","memory","learning",
            "perception","emotion","personality","disorder","therapy","freud","piaget",
            "pavlov","skinner","maslow","erikson","social","developmental","clinical",
            "anxiety","depression","stress","motivation","intelligence","consciousness",
            "unconscious","cognitive","behavioral","neuroscience","brain","attachment",
            "schizophrenia","bipolar","autism","adhd","ocd","ptsd","phobia","addiction",
            "milgram","zimbardo","bandura","ainsworth","bowlby","rogers","jung","adler",
            "iq","eq","nature nurture","twin study","case study","experiment","survey"
        ],
        "system_prompt": """You are a Psychology tutor. Answer the psychology question thoroughly.
- Answer exactly what was asked
- Name the relevant theory/study concisely
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "philosophy": {
        "name": "Philosophy Expert", "icon": "🤔",
        "keywords": [
            "philosophy","ethics","morality","logic","epistemology","ontology",
            "metaphysics","plato","aristotle","kant","socrates","nietzsche","descartes",
            "hume","locke","rousseau","marx","existentialism","utilitarianism",
            "deontology","virtue","truth","knowledge","reality","consciousness",
            "free will","determinism","argument","fallacy","reasoning","aesthetics",
            "mind","justice","rights","duty","evil","god","existence","soul",
            "personal identity","causation","induction","empiricism","rationalism",
            "stoicism","buddhism","confucianism","taoism","political philosophy"
        ],
        "system_prompt": """You are a Philosophy tutor. Answer the philosophy question thoroughly.
- Answer exactly what was asked, clearly and concisely
- Define key terms briefly
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "mathematics_advanced": {
        "name": "Advanced Math Expert", "icon": "∑",
        "keywords": [
            "real analysis","topology","abstract algebra","group theory","ring","field",
            "galois","measure theory","functional analysis","complex analysis","manifold",
            "differential geometry","algebraic geometry","number theory","combinatorics",
            "graph theory","category theory","set theory","proof","theorem","lemma",
            "corollary","conjecture","fourier","laplace","z-transform","pde","ode",
            "stochastic","markov","hilbert space","banach","lebesgue","riemann zeta",
            "prime number theorem","cryptography","coding theory","information theory"
        ],
        "system_prompt": """You are an Advanced Mathematics tutor. Answer ONLY the specific question asked.
- Answer exactly what was asked with rigorous working
- State definitions and theorems used
- If retrieved context is relevant, use it; otherwise answer from your own knowledge
- Feel free to add helpful related detail — do not artificially shorten your answer"""
    },

    "programming": {
        "name": "Programming Expert", "icon": "👨‍💻",
        "keywords": [
            "code","program","script","function","bug","debug","error","exception",
            "python","javascript","java","react","node","api","framework","library",
            "syntax","compile","runtime","variable","loop","class","object","array",
            "git","github","deploy","build","package","npm","pip","ide","vscode",
            "algorithm","leetcode","interview","coding question","write a function",
            "fix this code","stack trace","import","module","dependency"
        ],
        "system_prompt": """You are an expert software engineer and coding mentor.
- Give detailed, well-explained answers with working code examples and comments
- Explain the reasoning behind the approach, not just the code
- Mention edge cases, best practices, and alternatives where useful
- If the user shares broken code, explain the bug and show the fix
- Be thorough — a few sentences is rarely enough for a coding question"""
    },

    "technology": {
        "name": "Technology Expert", "icon": "📱",
        "keywords": [
            "technology","tech","gadget","smartphone","laptop","software","hardware",
            "app","application","ai","artificial intelligence","chatgpt","gpu","cpu",
            "processor","cloud","saas","startup","silicon valley","iphone","android",
            "windows","macos","linux os","update","feature","launch","release",
            "company","ceo of","product","device","wearable","vr","5g","chip"
        ],
        "system_prompt": """You are a knowledgeable technology analyst and explainer.
- Give detailed, well-rounded answers covering how things work, why they matter, and context
- Compare options when relevant (pros/cons, alternatives)
- Use plain language but don't oversimplify — include specifics, numbers, and examples
- Be thorough and informative, not just a one-line definition"""
    },

    "finance": {
        "name": "Finance Expert", "icon": "💰",
        "keywords": [
            "finance","money","invest","investment","stock","stocks","share","mutual fund",
            "bond","portfolio","budget","saving","savings","tax","taxes","loan","interest rate",
            "mortgage","credit","debit","bank","banking","cryptocurrency","crypto","bitcoin",
            "trading","market","economy","inflation","recession","retirement","insurance",
            "salary","income","expense","financial planning","compound interest","roi"
        ],
        "system_prompt": """You are a knowledgeable finance and personal finance explainer.
- Give detailed, educational explanations covering concepts, mechanics, and real examples
- Explain trade-offs and risks where relevant
- You may discuss general financial concepts and strategies, but make clear you are not a licensed financial advisor for personalized investment/legal/tax advice
- Be thorough — include relevant numbers, formulas, or examples"""
    },

    "career": {
        "name": "Career Guidance Expert", "icon": "💼",
        "keywords": [
            "career","job","resume","cv","interview","interview question","job search",
            "linkedin","cover letter","promotion","salary negotiation","internship",
            "skills","职业","work experience","portfolio","networking","job offer",
            "career change","career path","professional development","workplace",
            "manager","employer","hiring","recruiter","job description"
        ],
        "system_prompt": """You are an experienced career coach and mentor.
- Give detailed, actionable, and encouraging advice
- Include concrete examples, frameworks, or step-by-step approaches
- Tailor advice to the situation described; ask clarifying questions only if essential
- Be thorough — career questions deserve nuanced, complete answers"""
    },

    "entertainment": {
        "name": "Entertainment Expert", "icon": "🎬",
        "keywords": [
            "movie","movies","film","films","recommend a movie","suggest a film","actor","actress","director","tv show",
            "series","netflix","anime","music","song","album","artist","band","concert",
            "celebrity","award","oscar","grammy","box office","trailer","sequel",
            "season","episode","cast","plot","review","genre","streaming","game",
            "video game","gaming","novel","book series"
        ],
        "system_prompt": """You are a knowledgeable entertainment and pop-culture expert.
- Give detailed, engaging answers about movies, TV, music, games, and celebrities
- Include relevant background, context, trivia, and recommendations when useful
- If asked for opinions (e.g. "is X good"), give a balanced, informative take
- Be thorough and conversational — entertainment topics benefit from rich detail"""
    },

    "science": {
        "name": "Science Expert", "icon": "🔬",
        "keywords": [
            "science","scientific","experiment","hypothesis","theory","research",
            "space","nasa","universe","planet","galaxy","astronomy","climate",
            "environment","ecosystem","species","evolution theory","genetics",
            "vaccine","medicine","disease","virus","bacteria","brain science",
            "discovery","study finds","scientists"
        ],
        "system_prompt": """You are a knowledgeable science communicator covering all scientific fields.
- Give detailed, accurate explanations with relevant mechanisms, examples, and context
- Connect concepts to real-world relevance where helpful
- Be thorough and clear — break down complex ideas into understandable parts without losing depth"""
    },

    "current_affairs": {
        "name": "Current Affairs Expert", "icon": "📰",
        "keywords": [
            "news","current events","latest","recent","today","this week","politics",
            "election","government","president","prime minister","policy","war",
            "conflict","international","world news","economy news","headline",
            "breaking","update on","what happened","situation in"
        ],
        "system_prompt": """You are a knowledgeable current affairs and general news explainer.
- Give detailed, balanced, and factual explanations of events, policies, and contexts
- Present multiple perspectives on contested topics rather than taking sides
- Note that your knowledge may not include the very latest events — say so if relevant
- Be thorough — provide background and context, not just a headline summary"""
    },

    "general_chat": {
        "name": "Chat Companion", "icon": "💬",
        "keywords": [
            "hi","hello","hey","how are you","what's up","thanks","thank you",
            "good morning","good night","joke","funny","tell me a story","chat",
            "talk to me","bored","feeling","opinion","what do you think","fun fact",
            "riddle","recommend","suggestion"
        ],
        "system_prompt": """You are a warm, friendly, and engaging conversational companion.
- Respond naturally and conversationally, matching the user's tone
- Feel free to be detailed, share interesting context, or ask follow-up questions
- For casual chat, keep it light but still engaging — share interesting tidbits when relevant"""
    },

    "health_lifestyle": {
        "name": "Health & Lifestyle Expert", "icon": "🏥",
        "keywords": [
            "skin","skincare","acne","moisturizer","sunscreen","serum","face wash",
            "hair","haircare","hair fall","dandruff","shampoo","conditioner",
            "diet","nutrition","weight loss","weight gain","lose weight","gain weight","calories","protein",
            "exercise","workout","fitness","gym","yoga","meditation",
            "sleep","stress","anxiety","mental health","depression","wellness",
            "vitamins","supplements","immunity","health tips","home remedy",
            "period","menstrual","hormones","thyroid","diabetes","blood pressure",
            "teeth","dental","eye care","body care","hygiene","beauty",
            "pregnancy","pcod","pcos","fertility"
        ],
        "system_prompt": """You are an expert in health, wellness, skincare, haircare, nutrition, and lifestyle.
- Give practical, evidence-based advice on skincare routines, ingredients, and concerns (acne, oiliness, dryness, pigmentation etc.)
- Cover haircare, diet, fitness, mental wellness, and general health topics in detail
- Recommend routines, ingredients to look for/avoid, and lifestyle changes
- Always mention when a doctor or dermatologist should be consulted for serious concerns
- Be friendly, detailed, and actionable — give real recommendations, not vague answers"""
    },

    "general_knowledge": {
        "name": "General Knowledge Expert", "icon": "🌐",
        "keywords": [
            "what is","who is","who was","when did","where is","define","explain",
            "meaning of","fact about","history of","capital of","population of",
            "how does","why does","difference between","compare","general knowledge",
            "how to","how do i","can you","tell me","give me","help me","i want to",
            "cook","recipe","food","meal","dinner","lunch","breakfast","bake","kitchen",
            "travel","trip","visit","country","city","place","destination","hotel","flight",
            "meditate","mindfulness","spiritual","habit","routine","lifestyle","self improvement",
            "relationship","friendship","family","parenting","dating","marriage","social",
            "language","learn","study","tips","advice","guide","tutorial","how can i",
            "pet","animal","dog","cat","plant","garden","home","house","decor","diy",
            "fashion","clothes","style","outfit","dress","wear",
            "law","legal","rights","rule","policy","regulation"
        ],
        "system_prompt": """You are a knowledgeable, helpful assistant covering any topic — cooking, travel, lifestyle, relationships, general facts, or anything else.
- Answer every question helpfully and in detail regardless of topic
- Give practical, actionable advice with real examples
- Never refuse or say "that's not my area" — you cover everything
- Be warm, clear, and thorough"""
    },

    "general": {
        "name": "General Expert", "icon": "🎓",
        "keywords": [],
        "system_prompt": """You are a helpful, knowledgeable AI assistant. Answer any question on any topic — academics, cooking, travel, lifestyle, relationships, health, technology, entertainment, or anything else.
- Always give a helpful, detailed answer. Never refuse or say a topic is outside your scope.
- Be practical and clear. Use examples where helpful.
- If the question is factual, be accurate. If it is advice, be actionable."""
    }
}


class MoERouter:
    """Keyword-weighted router that selects the best expert for each query."""

    def route(self, query: str) -> str:
        q_lower = query.lower()
        scores = {}
        for expert_id, expert in EXPERTS.items():
            if expert_id in ("general", "general_knowledge"):
                continue
            score = sum(
                (3 if len(kw) > 10 else 2 if len(kw) > 6 else 1)
                for kw in expert["keywords"]
                if kw in q_lower
            )
            scores[expert_id] = score

        if not scores:
            return "general_knowledge"
        best = max(scores, key=scores.get)
        # If no specialist matched, route to general_knowledge (handles any topic)
        if scores[best] == 0:
            return "general_knowledge"
        return best


# ── Comprehensive Knowledge Base (150+ entries across 13 subjects) ───────────
KNOWLEDGE_BASE = [
    # ── MATHEMATICS ──────────────────────────────────────────────────────────
    {"id": "math_001", "text": "Pythagorean theorem: In a right triangle a²+b²=c² where c is the hypotenuse. Used to find unknown side lengths and distances.", "subject": "mathematics"},
    {"id": "math_002", "text": "Derivative rules: Power d/dx(xⁿ)=nxⁿ⁻¹, Product d/dx(fg)=f'g+fg', Quotient d/dx(f/g)=(f'g-fg')/g², Chain d/dx(f(g))=f'(g)·g'. Common: d/dx(sin x)=cos x, d/dx(eˣ)=eˣ, d/dx(ln x)=1/x.", "subject": "mathematics"},
    {"id": "math_003", "text": "Integration by parts: ∫u dv = uv − ∫v du. Choose u by LIATE: Logarithmic, Inverse trig, Algebraic, Trigonometric, Exponential. Common integrals: ∫sin x=-cos x, ∫eˣ=eˣ, ∫1/x=ln|x|.", "subject": "mathematics"},
    {"id": "math_004", "text": "Quadratic formula: x=(−b±√(b²−4ac))/2a for ax²+bx+c=0. Discriminant Δ=b²−4ac: >0 two real roots, =0 one root (repeated), <0 no real roots (complex). Sum of roots=-b/a, product=c/a.", "subject": "mathematics"},
    {"id": "math_005", "text": "Matrix operations: Addition requires same dimensions. Multiplication: (AB)ᵢⱼ=Σ Aᵢₖ·Bₖⱼ, requires columns_A=rows_B. Determinant 2×2: det[[a,b],[c,d]]=ad-bc. Inverse: A⁻¹=adj(A)/det(A).", "subject": "mathematics"},
    {"id": "math_006", "text": "Bayes' theorem: P(A|B)=P(B|A)·P(A)/P(B). Total probability: P(B)=ΣP(B|Aᵢ)P(Aᵢ). Foundation of Bayesian inference and Naive Bayes classifier.", "subject": "mathematics"},
    {"id": "math_007", "text": "Taylor series: f(x)=Σf⁽ⁿ⁾(a)/n!·(x-a)ⁿ. Maclaurin: eˣ=1+x+x²/2!+x³/3!+..., sin x=x-x³/3!+x⁵/5!-..., cos x=1-x²/2!+x⁴/4!-..., ln(1+x)=x-x²/2+x³/3-...", "subject": "mathematics"},
    {"id": "math_008", "text": "Trigonometry identities: sin²x+cos²x=1, tan x=sin x/cos x, sin 2x=2 sin x cos x, cos 2x=cos²x-sin²x=1-2sin²x, sin(A±B)=sin A cos B±cos A sin B.", "subject": "mathematics"},
    {"id": "math_009", "text": "Binomial theorem: (a+b)ⁿ=ΣC(n,k)aⁿ⁻ᵏbᵏ. C(n,k)=n!/(k!(n-k)!). Pascal's triangle gives coefficients. For statistics: P(X=k)=C(n,k)pᵏ(1-p)ⁿ⁻ᵏ (Binomial distribution).", "subject": "mathematics"},
    {"id": "math_010", "text": "Eigenvalues/Eigenvectors: det(A-λI)=0 gives eigenvalues. Av=λv gives eigenvectors. Used in PCA, Google PageRank, quantum mechanics, principal axes of inertia.", "subject": "mathematics"},
    {"id": "math_011", "text": "Limits: L'Hôpital's rule for 0/0 or ∞/∞: lim f/g = lim f'/g'. Squeeze theorem. Standard limits: lim(sin x/x)=1 as x→0, lim(1+1/n)ⁿ=e as n→∞.", "subject": "mathematics"},
    {"id": "math_012", "text": "Permutations and Combinations: nPr=n!/(n-r)! (order matters), nCr=n!/(r!(n-r)!) (order doesn't matter). Circular permutations=(n-1)!. With repetition: nˢ permutations.", "subject": "mathematics"},

    # ── PHYSICS ──────────────────────────────────────────────────────────────
    {"id": "phys_001", "text": "Newton's laws: (1) Inertia: objects stay at rest/motion unless net force acts. (2) F=ma: net force=mass×acceleration. (3) Action-reaction: forces come in equal & opposite pairs.", "subject": "physics"},
    {"id": "phys_002", "text": "Kinematic equations (constant acceleration): v=u+at, s=ut+½at², v²=u²+2as, s=(u+v)t/2. For projectile motion: horizontal is uniform (a=0), vertical has a=g=9.8 m/s².", "subject": "physics"},
    {"id": "phys_003", "text": "Energy: KE=½mv², PE=mgh, elastic PE=½kx². Work-energy theorem: W_net=ΔKE. Power P=W/t=Fv. Conservation of energy: ΔKE+ΔPE+ΔHeat=0 (closed system).", "subject": "physics"},
    {"id": "phys_004", "text": "Ohm's Law: V=IR. Power: P=VI=I²R=V²/R. Series: R_total=R1+R2+..., same current. Parallel: 1/R_total=1/R1+1/R2+..., same voltage. Kirchhoff's laws: ΣV=0 (loop), ΣI=0 (node).", "subject": "physics"},
    {"id": "phys_005", "text": "Waves: v=fλ. Period T=1/f. Sound in air ≈340 m/s. Electromagnetic spectrum (low→high f): radio, microwave, IR, visible, UV, X-ray, gamma. Doppler effect: f_obs=f_s(v±v_obs)/(v∓v_s).", "subject": "physics"},
    {"id": "phys_006", "text": "Thermodynamics laws: 0th: thermal equilibrium. 1st: ΔU=Q-W (energy conservation). 2nd: entropy S always increases in isolated systems; heat flows hot→cold. 3rd: S→0 as T→0 K.", "subject": "physics"},
    {"id": "phys_007", "text": "Gravitation: F=Gm₁m₂/r², G=6.674×10⁻¹¹ Nm²/kg². Surface gravity g=GM/R². Orbital speed v=√(GM/r). Escape velocity v_e=√(2GM/R). Gravitational PE=−GMm/r.", "subject": "physics"},
    {"id": "phys_008", "text": "Modern Physics: Photoelectric effect E=hf-φ. de Broglie wavelength λ=h/mv. Heisenberg uncertainty: ΔxΔp≥ℏ/2. Bohr model: E_n=-13.6/n² eV for hydrogen. E=mc² (mass-energy equivalence).", "subject": "physics"},
    {"id": "phys_009", "text": "Special relativity: Time dilation: t'=t/√(1-v²/c²). Length contraction: L'=L√(1-v²/c²). Relativistic mass increases. Simultaneity is relative. Nothing with mass exceeds c.", "subject": "physics"},
    {"id": "phys_010", "text": "Electromagnetic induction: Faraday's law: EMF=−dΦ/dt. Lenz's law: induced current opposes change. Transformers: V_s/V_p=N_s/N_p. AC generator converts mechanical→electrical energy.", "subject": "physics"},

    # ── COMPUTER SCIENCE ─────────────────────────────────────────────────────
    {"id": "cs_001", "text": "Big O notation: O(1) constant (hash lookup), O(log n) binary search, O(n) linear scan, O(n log n) merge/quick sort, O(n²) bubble/selection sort, O(2ⁿ) subsets, O(n!) permutations.", "subject": "computer_science"},
    {"id": "cs_002", "text": "Binary search algorithm: Compare middle element; if equal return; if target < mid search left half; else search right half. Time O(log n), Space O(1). Requires sorted array.", "subject": "computer_science"},
    {"id": "cs_003", "text": "Dynamic programming: Overlapping subproblems + optimal substructure. Memoization (top-down with cache). Tabulation (bottom-up with table). Examples: Fibonacci, 0-1 knapsack, LCS, edit distance, coin change.", "subject": "computer_science"},
    {"id": "cs_004", "text": "Graph algorithms: BFS (queue, shortest path unweighted), DFS (stack/recursion, cycles/connectivity), Dijkstra (priority queue, shortest path weighted), Bellman-Ford (negative edges), Floyd-Warshall (all pairs).", "subject": "computer_science"},
    {"id": "cs_005", "text": "Python fundamentals: List comprehension [x*2 for x in range(10) if x%2==0]. Lambda: f=lambda x,y: x+y. *args (tuple), **kwargs (dict). Generators use yield. Decorators use @. f-strings: f'{value:.2f}'.", "subject": "computer_science"},
    {"id": "cs_006", "text": "OOP: Encapsulation (data hiding), Abstraction (interface hiding), Inheritance (code reuse, is-a), Polymorphism (same interface, different behavior). SOLID: Single responsibility, Open/closed, Liskov, Interface segregation, Dependency inversion.", "subject": "computer_science"},
    {"id": "cs_007", "text": "SQL: SELECT col FROM table WHERE cond GROUP BY col HAVING cond ORDER BY col LIMIT n. JOINs: INNER (matching), LEFT (all left+matching right), FULL OUTER. Indexes speed up reads; slow writes. ACID: Atomicity, Consistency, Isolation, Durability.", "subject": "computer_science"},
    {"id": "cs_008", "text": "REST API: GET(read), POST(create), PUT(replace), PATCH(update), DELETE(remove). Status codes: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error.", "subject": "computer_science"},
    {"id": "cs_009", "text": "Sorting: Bubble O(n²) stable, Selection O(n²) unstable, Insertion O(n²) good for small/nearly sorted, Merge O(n log n) stable divide-conquer, Quick O(n log n) avg/O(n²) worst unstable, Heap O(n log n) unstable in-place.", "subject": "computer_science"},
    {"id": "cs_010", "text": "Neural networks: Layers: input→hidden(s)→output. Activations: ReLU=max(0,x), Sigmoid=1/(1+e⁻ˣ), Tanh, Softmax for multi-class. Backprop computes gradients via chain rule. Loss: MSE for regression, Cross-entropy for classification.", "subject": "computer_science"},
    {"id": "cs_011", "text": "Git workflow: init/clone → add → commit -m 'msg' → push. Branching: branch → checkout → merge/rebase. Undo: revert (safe, new commit), reset --hard (destructive). Pull request = code review before merge.", "subject": "computer_science"},
    {"id": "cs_012", "text": "React hooks: useState(initialValue) for state, useEffect(fn,[deps]) for side effects (fetch, subscriptions), useContext for global state, useRef for DOM access, useMemo/useCallback to prevent unnecessary re-renders.", "subject": "computer_science"},
    {"id": "cs_013", "text": "Data structures: Array O(1) access, O(n) insert. Linked list O(n) access, O(1) insert at head. Stack (LIFO): push/pop O(1). Queue (FIFO): enqueue/dequeue O(1). Hash table O(1) avg for all ops. BST O(log n) balanced.", "subject": "computer_science"},
    {"id": "cs_014", "text": "System design concepts: Load balancing (distributes traffic), Caching (Redis, Memcached), Database sharding (horizontal partitioning), Replication (read replicas), CDN (static assets), Message queues (Kafka, RabbitMQ) for async processing.", "subject": "computer_science"},

    # ── CHEMISTRY ────────────────────────────────────────────────────────────
    {"id": "chem_001", "text": "Balancing equations: Equal atoms on both sides using coefficients (never change subscripts). For redox: use half-reaction method—balance O with H₂O, H with H⁺, charge with electrons, then combine.", "subject": "chemistry"},
    {"id": "chem_002", "text": "pH scale: pH=−log[H⁺]. pH<7 acidic, =7 neutral, >7 basic. pOH=−log[OH⁻]. pH+pOH=14 at 25°C. Henderson-Hasselbalch: pH=pKa+log([A⁻]/[HA]). Buffer works best when pH≈pKa.", "subject": "chemistry"},
    {"id": "chem_003", "text": "Mole concept: 1 mol=6.022×10²³ particles (Avogadro's). Molar mass=g/mol (from periodic table). n=m/M. Molarity M=n/V(L). Dilution: M₁V₁=M₂V₂. Ideal gas: PV=nRT (R=8.314 J/mol·K).", "subject": "chemistry"},
    {"id": "chem_004", "text": "Organic functional groups: Alkane -C-C- (saturated), Alkene C=C (unsaturated), Alkyne C≡C, Alcohol -OH, Aldehyde -CHO, Ketone C=O, Carboxylic acid -COOH, Ester -COO-, Amine -NH₂, Amide -CONH₂.", "subject": "chemistry"},
    {"id": "chem_005", "text": "Chemical equilibrium: Kc=[products]^p/[reactants]^r (omit solids/pure liquids). Le Chatelier: add reactant→shifts right; add product→shifts left; increase P→shifts to fewer moles gas; increase T→shifts endothermic direction.", "subject": "chemistry"},
    {"id": "chem_006", "text": "Electrochemistry: Anode=oxidation (loses e⁻), Cathode=reduction (gains e⁻). EMF=E°cathode−E°anode. Spontaneous if EMF>0, ΔG<0. Faraday: Q=nF=It. Electrolysis: non-spontaneous reaction driven by electricity.", "subject": "chemistry"},
    {"id": "chem_007", "text": "Periodic trends: Atomic radius: decreases left→right (more protons pull e⁻ closer), increases top→bottom (more shells). Electronegativity: F highest. Ionization energy: inverse of atomic radius. Metallic character decreases left→right.", "subject": "chemistry"},
    {"id": "chem_008", "text": "Thermochemistry: Hess's law: ΔH_rxn=ΣΔH_f(products)−ΣΔH_f(reactants). Exothermic ΔH<0, endothermic ΔH>0. Gibbs: ΔG=ΔH−TΔS. Spontaneous if ΔG<0. Entropy S: disorder measure; solids<liquids<gases.", "subject": "chemistry"},

    # ── BIOLOGY ──────────────────────────────────────────────────────────────
    {"id": "bio_001", "text": "DNA replication: Semiconservative. Helicase unwinds double helix, SSBPs stabilize, primase adds RNA primer, DNA polymerase III synthesizes 5'→3', ligase seals Okazaki fragments. Leading strand continuous, lagging strand discontinuous.", "subject": "biology"},
    {"id": "bio_002", "text": "Central dogma: DNA→(transcription)→mRNA→(translation)→Protein. Transcription: RNA polymerase reads template 3'→5', produces mRNA 5'→3'. Translation: ribosome reads codons (3 bases), tRNA brings amino acids, peptide bonds form.", "subject": "biology"},
    {"id": "bio_003", "text": "Photosynthesis: 6CO₂+6H₂O+light→C₆H₁₂O₆+6O₂. Light reactions (thylakoid): water splits, O₂ released, ATP+NADPH made, excited electrons flow ETC. Calvin cycle (stroma): CO₂ fixed by RuBisCO, ATP+NADPH used to make G3P.", "subject": "biology"},
    {"id": "bio_004", "text": "Cellular respiration: C₆H₁₂O₆+6O₂→6CO₂+6H₂O+ATP. Glycolysis (cytoplasm, 2ATP net), Pyruvate oxidation (mitochondria), Krebs/Citric acid cycle (8ATP/glucose), ETC/Oxidative phosphorylation (≈28 ATP). Total: ~30-32 ATP.", "subject": "biology"},
    {"id": "bio_005", "text": "Mendelian genetics: Dominant allele masks recessive. Monohybrid Aa×Aa: 1AA:2Aa:1aa genotype (3:1 phenotype). Dihybrid AaBb×AaBb: 9:3:3:1 ratio. Law of segregation: alleles separate in meiosis. Independent assortment: genes on different chromosomes.", "subject": "biology"},
    {"id": "bio_006", "text": "Cell division: Mitosis (PMAT): Prophase→Metaphase→Anaphase→Telophase+Cytokinesis. Produces 2 identical diploid cells. Meiosis I+II: 4 haploid cells with genetic recombination. Crossing over in prophase I creates genetic diversity.", "subject": "biology"},
    {"id": "bio_007", "text": "Immune system: Innate (non-specific, fast): physical barriers (skin), phagocytes, NK cells, inflammation, fever. Adaptive (specific, slower): B cells produce antibodies (humoral), T cells (cellular—helper CD4+ coordinates; cytotoxic CD8+ kills). Memory cells provide lasting immunity.", "subject": "biology"},
    {"id": "bio_008", "text": "Evolution: Natural selection: heritable variation + differential survival/reproduction → adaptation. Evidence: fossils, comparative anatomy (homologous structures), molecular biology (DNA similarity), biogeography. Speciation: allopatric (geographic isolation), sympatric.", "subject": "biology"},
    {"id": "bio_009", "text": "Human skeleton: An adult human body has exactly 206 bones. A newborn baby has ~270-300 bones which fuse over time down to 206 by adulthood. Major regions: skull (22), vertebral column/spine (26), ribs+sternum (25), shoulder girdle (4), arms (6), wrists+hands (54), pelvis (2), legs (8), ankles+feet (52), others. The femur (thigh bone) is the longest bone. The stapes in the ear is the smallest bone.", "subject": "biology"},
    {"id": "bio_010", "text": "Human body facts: Heart beats ~60-100 times/min, pumps ~5L blood/min. Lungs: 2 (left has 2 lobes, right has 3). Muscles: ~600-650 skeletal muscles. Organs: liver is largest internal organ. Brain weighs ~1.4kg, has ~86 billion neurons. Blood: average adult has ~5 litres. Kidneys filter ~200L blood daily. Teeth: adults have 32 teeth (including 4 wisdom teeth).", "subject": "biology"},
    {"id": "bio_011", "text": "Human digestive system: Mouth→Oesophagus→Stomach→Small intestine (duodenum, jejunum, ileum, ~6m)→Large intestine (~1.5m)→Rectum→Anus. Liver produces bile; pancreas secretes digestive enzymes and insulin/glucagon. Small intestine absorbs nutrients; large intestine absorbs water. Total GI tract length ~9 metres.", "subject": "biology"},
    {"id": "bio_012", "text": "Human nervous system: Central NS (brain + spinal cord) + Peripheral NS (somatic + autonomic). Brain regions: cerebrum (cognition), cerebellum (balance/coordination), brainstem (vital functions). Neuron structure: dendrites→cell body→axon→synapse. Signal transmission: electrical impulse (action potential) + chemical (neurotransmitters: dopamine, serotonin, acetylcholine).", "subject": "biology"},

    # ── HISTORY ──────────────────────────────────────────────────────────────
    {"id": "hist_001", "text": "World War I (1914-1918): MAIN causes—Militarism, Alliance system (Triple Alliance vs Triple Entente), Imperialism, Nationalism. Trigger: assassination of Archduke Franz Ferdinand (Sarajevo, 1914). Trench warfare, poison gas. Treaty of Versailles 1919.", "subject": "history"},
    {"id": "hist_002", "text": "World War II (1939-1945): Hitler's expansionism, appeasement failure. Germany invaded Poland Sep 1939. Holocaust: 6 million Jews murdered. Key events: Battle of Britain, Operation Barbarossa, Pearl Harbor, D-Day 1944. Ended: VE Day May 8, VJ Day Aug 15 1945.", "subject": "history"},
    {"id": "hist_003", "text": "French Revolution (1789-1799): Causes: Estates inequality, Enlightenment ideas, financial crisis, food shortage. Storming of Bastille 14 July 1789. Declaration of Rights of Man. Reign of Terror (Robespierre). Directory. Led to Napoleon Bonaparte's rise.", "subject": "history"},
    {"id": "hist_004", "text": "Indian Independence (1947): British East India Company rule from 1757, Crown rule 1858. 1857 Sepoy Mutiny. Gandhi's non-violence (satyagraha), Non-Cooperation (1920), Salt March (1930), Quit India (1942). Independence + Partition 15 Aug 1947. Nehru PM, Jinnah Pakistan.", "subject": "history"},
    {"id": "hist_005", "text": "Cold War (1947-1991): USA (capitalism/democracy) vs USSR (communism) ideological conflict. Key events: Berlin Blockade 1948, NATO 1949, Korean War 1950-53, Sputnik 1957, Cuban Missile Crisis 1962, Vietnam War, détente, Berlin Wall fall 1989, USSR collapse 1991.", "subject": "history"},
    {"id": "hist_006", "text": "Ancient Rome: Founded 753 BCE (legend). Republic 509-27 BCE. Julius Caesar dictator, assassinated 44 BCE. Augustus first emperor 27 BCE. Pax Romana. Peak under Trajan. Fall of Western Empire 476 CE. Legacy: Roman law, Latin, Christianity, engineering (roads, aqueducts).", "subject": "history"},
    {"id": "hist_007", "text": "Industrial Revolution (c.1760-1840): Started Britain. Key innovations: steam engine (Watt), spinning jenny (Hargreaves), power loom, iron smelting (coke). Effects: urbanization, factory system, capitalism, child labor, Luddites, trade unions, pollution.", "subject": "history"},
    {"id": "hist_008", "text": "American Revolution (1775-1783): Causes: taxation without representation (Stamp Act, Tea Act), Enlightenment ideas, Boston Massacre/Tea Party. Declaration of Independence 4 July 1776 (Jefferson). Valley Forge. Yorktown 1781. Constitution 1787. Bill of Rights 1791.", "subject": "history"},
    {"id": "hist_009", "text": "Ancient India: Indus Valley Civilization c.2500 BCE. Vedic period (1500-500 BCE). Maurya Empire (Chandragupta, Ashoka). Gupta Empire 'Golden Age' (science, literature, mathematics, decimal system). Bhakti movement. Delhi Sultanate. Mughal Empire (Akbar to Aurangzeb).", "subject": "history"},
    {"id": "hist_010", "text": "Renaissance (14th-17th century): Revival of classical learning. Italy first (Florence—Medici patronage). Art: Leonardo da Vinci, Michelangelo, Raphael. Literature: Dante, Petrarch, Machiavelli. Science: Copernicus, Galileo. Printing press (Gutenberg 1440) spread ideas.", "subject": "history"},

    # ── GEOGRAPHY ────────────────────────────────────────────────────────────
    {"id": "geo_001", "text": "Plate tectonics: 7 major plates + several minor. Convergent plates: oceanic-continental → subduction zone + volcano + trench; continental-continental → fold mountains (Himalayas). Divergent: rift valleys, mid-ocean ridges. Transform: earthquakes (San Andreas fault).", "subject": "geography"},
    {"id": "geo_002", "text": "River processes: Erosion (hydraulic action, abrasion, attrition, solution). Transportation (traction, saltation, suspension, solution). Deposition. Upper course: V-valleys, waterfalls. Middle: meanders. Lower: floodplains, oxbow lakes, deltas, levees.", "subject": "geography"},
    {"id": "geo_003", "text": "Climate zones: Tropical (0-23.5°): hot, wet, little seasonal variation. Desert (~30°): high pressure, less than 250mm rain. Mediterranean: hot dry summer, warm wet winter. Temperate: 4 seasons. Boreal (taiga): long cold winter, coniferous forest. Tundra: >66.5°, permafrost.", "subject": "geography"},
    {"id": "geo_004", "text": "Development indicators: HDI = life expectancy + education + income. GDP per capita (wealth). Birth/death rates (BR/DR). Infant mortality rate (IMR). Literacy rate. Access to clean water/sanitation. Gini coefficient measures inequality. LEDCs vs MEDCs vs NICs.", "subject": "geography"},
    {"id": "geo_005", "text": "Urbanization: >55% of world population in cities (2024). Push factors (rural poverty, lack of jobs, natural disasters). Pull factors (employment, services, higher wages). Megacities >10 million. Urban challenges: housing, traffic, pollution, inequality (shanty towns/favelas).", "subject": "geography"},
    {"id": "geo_006", "text": "Climate change: Global temperature risen ~1.2°C since pre-industrial. Causes: CO₂ from fossil fuels, deforestation, methane from agriculture/landfill. Effects: sea level rise, extreme weather, coral bleaching, species extinction, droughts, flooding.", "subject": "geography"},

    # ── ECONOMICS ────────────────────────────────────────────────────────────
    {"id": "econ_001", "text": "Supply and demand: Demand curve downward-sloping (price↑→demand↓). Supply curve upward-sloping. Equilibrium: intersection. Shifts: demand (income, preferences, prices of substitutes/complements, expectations). Supply (costs, technology, number of producers, taxes).", "subject": "economics"},
    {"id": "econ_002", "text": "GDP = C+I+G+(X-M): Consumption + Investment + Government spending + Net exports. Nominal GDP: current prices. Real GDP: constant prices (adjusts for inflation). GDP per capita: standard of living proxy. GNI includes income from abroad.", "subject": "economics"},
    {"id": "econ_003", "text": "Inflation: CPI measures average price level changes. Types: demand-pull (too much money chasing goods), cost-push (supply shocks like oil price rise), built-in (wage-price spiral). Effects: redistributes income, reduces purchasing power, uncertainty. Central bank raises interest rates to control.", "subject": "economics"},
    {"id": "econ_004", "text": "Elasticity: PED=%ΔQd/%ΔP. |PED|>1 elastic (luxuries, many substitutes), <1 inelastic (necessities, few substitutes). YED=%ΔQd/%ΔY: normal goods YED>0, inferior goods YED<0, luxury YED>1. PES=%ΔQs/%ΔP: inelastic in short run.", "subject": "economics"},
    {"id": "econ_005", "text": "Market structures: Perfect competition (homogeneous, price takers, no barriers, normal profit LR). Monopoly (price maker, high barriers, abnormal profit, market failure). Oligopoly (few firms, interdependence, game theory). Monopolistic competition (many firms, differentiated products).", "subject": "economics"},
    {"id": "econ_006", "text": "Fiscal policy: Government spending (G) and taxation (T). Expansionary: G↑ or T↓ to stimulate economy. Contractionary: G↓ or T↑ to cool economy. Multiplier effect: ΔGDP=ΔG×(1/(1-MPC)). Budget deficit when G>T; surplus when T>G.", "subject": "economics"},

    # ── LITERATURE & ENGLISH ─────────────────────────────────────────────────
    {"id": "lit_001", "text": "Literary devices: Metaphor (direct comparison 'life is a journey'), Simile (using like/as), Personification (giving human qualities), Alliteration (repeated consonants), Assonance (repeated vowels), Onomatopoeia (sound words), Hyperbole (exaggeration for effect).", "subject": "literature_english"},
    {"id": "lit_002", "text": "Essay structure: Introduction (hook → background context → clear thesis statement). Body paragraphs (topic sentence → evidence/quotation → analysis/explanation → link back to thesis). Conclusion (restate thesis differently → synthesize main points → broader significance/evaluation).", "subject": "literature_english"},
    {"id": "lit_003", "text": "Shakespeare: Tragedies—Hamlet (revenge, indecision), Macbeth (ambition, guilt), Othello (jealousy, manipulation), King Lear (power, madness). Comedies—A Midsummer Night's Dream, Much Ado. Sonnets 154: themes of love, time, beauty. Soliloquy reveals inner thoughts.", "subject": "literature_english"},
    {"id": "lit_004", "text": "Poetry analysis (SLAPT or SMILE): Structure (form, stanzas, line length, rhyme scheme), Language (word choice, imagery), Attitude/Tone (speaker's feelings), Purpose (message, theme), Techniques (literary devices). Always embed quotations and analyse specific word choices.", "subject": "literature_english"},
    {"id": "lit_005", "text": "English grammar: Active voice 'The dog bit the man' vs Passive 'The man was bitten'. Tenses: Simple (I go/went), Continuous (I am/was going), Perfect (I have/had gone). Complex sentence: main clause + subordinate clause. Commas in lists, after introductory phrases.", "subject": "literature_english"},
    {"id": "lit_006", "text": "Narrative techniques: First person narrator (intimacy, limited perspective), Third person omniscient (all-knowing, panoramic), Unreliable narrator, Stream of consciousness, Foreshadowing, In medias res (starting in middle of action), Flashback (analepsis), Frame narrative.", "subject": "literature_english"},

    # ── PSYCHOLOGY ───────────────────────────────────────────────────────────
    {"id": "psych_001", "text": "Maslow's hierarchy (1943): Physiological (food, water, sleep) → Safety → Love/Belonging → Esteem → Self-actualization. Deficiency needs (D-needs) must be met before growth needs (B-needs). Criticism: not universal, doesn't account for cultural differences.", "subject": "psychology"},
    {"id": "psych_002", "text": "Classical conditioning (Pavlov): US (unconditioned stimulus: food) → UR (salivation). NS+US paired → NS becomes CS (conditioned stimulus: bell) → CR (conditioned response). Extinction: CS without US. Spontaneous recovery. Generalization vs Discrimination.", "subject": "psychology"},
    {"id": "psych_003", "text": "Operant conditioning (Skinner): Positive reinforcement (add reward→behavior↑), Negative reinforcement (remove unpleasant→behavior↑), Positive punishment (add unpleasant→behavior↓), Negative punishment (remove reward→behavior↓). Schedules: fixed ratio/interval vs variable ratio/interval.", "subject": "psychology"},
    {"id": "psych_004", "text": "Memory models: Multi-store model (Atkinson & Shiffrin): Sensory→Short-term memory (7±2 items, 18-30s, displacement)→Long-term memory (unlimited capacity/duration). Working memory model (Baddeley): Central executive, Phonological loop, Visuo-spatial sketchpad, Episodic buffer.", "subject": "psychology"},
    {"id": "psych_005", "text": "Piaget's developmental stages: Sensorimotor (0-2: object permanence), Preoperational (2-7: symbolic thinking, egocentrism, conservation lack), Concrete Operational (7-11: conservation, logical thinking, less egocentric), Formal Operational (12+: abstract reasoning, hypothetical thinking).", "subject": "psychology"},
    {"id": "psych_006", "text": "Social influence: Milgram (1963) obedience—65% gave maximum 450V shock to authority. Zimbardo Stanford Prison Experiment—roles determine behavior. Asch conformity—36.8% conformed to wrong line judgments. Factors: unanimity, group size, expertise of authority.", "subject": "psychology"},

    # ── PHILOSOPHY ───────────────────────────────────────────────────────────
    {"id": "phil_001", "text": "Ethical theories: Consequentialism/Utilitarianism (Mill, Bentham): greatest happiness for greatest number, judge actions by outcomes. Deontology (Kant): duty-based, categorical imperative 'act only by maxims you could universalize'. Virtue Ethics (Aristotle): develop virtuous character (eudaimonia).", "subject": "philosophy"},
    {"id": "phil_002", "text": "Plato's Theory of Forms: Physical world is imperfect shadows of perfect abstract Forms. Form of the Good is highest. Allegory of the Cave: prisoners mistake shadows for reality; philosopher escapes to see the sun (Truth). Immortal soul recalls Forms (anamnesis).", "subject": "philosophy"},
    {"id": "phil_003", "text": "Descartes' method: Systematic doubt—doubt all beliefs that can possibly be doubted. Cogito ergo sum 'I think therefore I am' — first certainty. Mind-body dualism: immaterial mind (res cogitans) vs material body (res extensa). Rationalism: knowledge from reason, not just senses.", "subject": "philosophy"},
    {"id": "phil_004", "text": "Logical fallacies: Ad hominem (attacking person), Straw man (misrepresent position), False dilemma (only two options), Slippery slope (unwarranted consequence chain), Post hoc (correlation = causation), Begging the question (circular reasoning), Appeal to authority, Red herring.", "subject": "philosophy"},
    {"id": "phil_005", "text": "Epistemology: What can we know? Rationalism (Descartes, Leibniz): innate ideas, reason as primary source. Empiricism (Locke, Hume): mind is tabula rasa, all knowledge from experience. Kant: synthesis—pure intuitions (space/time) + categories of understanding structure experience.", "subject": "philosophy"},

    # ── GEOGRAPHY extra ───────────────────────────────────────────────────────
    {"id": "geo_007", "text": "Natural hazards: Earthquakes: tectonic plate movement, measured by Richter scale. Volcanoes: magma from mantle, shield (gentle) vs composite (explosive). Tropical storms: form over warm ocean (>26°C), need Coriolis effect, bring extreme rain/wind. Preparation reduces deaths.", "subject": "geography"},
    {"id": "geo_008", "text": "Globalisation: Increased interconnectedness via trade, technology, culture, migration. TNCs operate in multiple countries (Nike, Apple). Benefits: economic growth, technology transfer, jobs. Costs: exploitation of cheap labor, tax avoidance, cultural homogenisation, environmental damage.", "subject": "geography"},
]




class RAGService:
    _instance = None

    def __init__(self):
        print("🔄 Initializing RAG service...")
        self.ready = False
        self.router = MoERouter()
        self.embedder = None
        self.collection = None

        # Configure Gemini
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
            print("  ⚠️  GEMINI_API_KEY not set! Set it in backend/.env")
            self.gemini_client = None
        else:
            self.gemini_client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options=genai_types.HttpOptions(api_version="v1beta"),
            )
            print(f"  ✅ Gemini configured — model: {settings.GEMINI_MODEL}")

        # Load sentence-transformers embedder
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            print("  ✅ Embedding model loaded")
        except Exception as e:
            print(f"  ⚠️  Embedding model failed to load: {e}")

        # Load ChromaDB
        try:
            import os
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name="edu_knowledge_v3",
                metadata={"hnsw:space": "cosine"},
            )
            print(f"  ✅ ChromaDB ready ({self.collection.count()} chunks)")
            if self.embedder:
                self._seed_knowledge()
        except Exception as e:
            print(f"  ⚠️  ChromaDB failed: {e}")

        self.ready = True
        print(f"✅ RAG service ready — Gemini model: {settings.GEMINI_MODEL}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            try:
                cls._instance = cls()
            except Exception as e:
                print(f"❌ RAGService failed to initialize: {e}")
                # Return a minimal stub so the server keeps running
                stub = object.__new__(cls)
                stub.ready = False
                stub.router = MoERouter()
                stub.embedder = None
                stub.collection = None
                cls._instance = stub
        return cls._instance

    def _seed_knowledge(self):
        """Add any missing knowledge chunks to ChromaDB."""
        try:
            result = self.collection.get(include=[])
            existing_ids = set(result.get("ids", []))
        except Exception:
            existing_ids = set()

        new_entries = [k for k in KNOWLEDGE_BASE if k["id"] not in existing_ids]
        if not new_entries:
            return

        BATCH = 32
        for i in range(0, len(new_entries), BATCH):
            batch = new_entries[i:i + BATCH]
            try:
                texts = [k["text"] for k in batch]
                embeddings = self.embedder.encode(texts, show_progress_bar=False).tolist()
                self.collection.add(
                    ids=[k["id"] for k in batch],
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=[{"subject": k["subject"]} for k in batch],
                )
            except Exception as e:
                print(f"  ⚠️  Seed batch error: {e}")
        print(f"  📚 Added {len(new_entries)} knowledge chunks to ChromaDB")

    def retrieve(self, query: str, expert_id: str, n_results: int = 4) -> list:
        """Retrieve relevant chunks from ChromaDB."""
        if not self.embedder or not self.collection:
            return []
        try:
            total = self.collection.count()
            if total == 0:
                return []

            query_embedding = self.embedder.encode([query])[0].tolist()

            # Subject-specific subjects map
            subject_map = {
                "mathematics": "mathematics",
                "mathematics_advanced": "mathematics",
                "physics": "physics",
                "computer_science": "computer_science",
                "chemistry": "chemistry",
                "biology": "biology",
                "history": "history",
                "geography": "geography",
                "economics": "economics",
                "literature_english": "literature_english",
                "psychology": "psychology",
                "philosophy": "philosophy",
                # New multi-domain experts have no curated KB yet —
                # skip retrieval entirely for them (faster, falls back to base LLM)
            }
            NO_RAG_EXPERTS = {
                "programming", "technology", "finance", "career",
                "entertainment", "science", "current_affairs",
                "general_chat", "general_knowledge", "health_lifestyle",
            }
            if expert_id in NO_RAG_EXPERTS:
                return []  # skip embedding + ChromaDB query entirely → lower latency

            results = []
            subject = subject_map.get(expert_id)
            n = min(n_results, total)

            # Try subject-specific first
            if subject:
                try:
                    res = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n,
                        where={"subject": subject},
                    )
                    docs = res.get("documents", [[]])[0]
                    dists = res.get("distances", [[]])[0]
                    results = [
                        {"text": d, "score": round(1 - dist, 3)}
                        for d, dist in zip(docs, dists)
                        if (1 - dist) > 0.35   # only high-relevance chunks
                    ]
                except Exception:
                    pass

            # Broad fallback if not enough results
            if len(results) < 2:
                try:
                    res = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n,
                    )
                    seen = {r["text"] for r in results}
                    docs = res.get("documents", [[]])[0]
                    dists = res.get("distances", [[]])[0]
                    for d, dist in zip(docs, dists):
                        if d not in seen and (1 - dist) > 0.35:
                            results.append({"text": d, "score": round(1 - dist, 3)})
                            seen.add(d)
                except Exception:
                    pass

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:n_results]
        except Exception as e:
            print(f"  ⚠️  Retrieval error: {e}")
            return []

    async def _call_gemini(self, system_prompt: str, messages: list) -> str:
        """Call Gemini API with streaming + truncation detection."""
        import asyncio

        if not self.gemini_client:
            raise ValueError("Gemini client not initialized — check GEMINI_API_KEY in .env")

        # Build contents list for the SDK
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append(genai_types.Content(
                role=role,
                parts=[genai_types.Part(text=msg["content"])]
            ))

        config = genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
            max_output_tokens=8192,
            top_p=0.9,
            thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
        )

        def _stream():
            import time
            max_retries = 3
            retry_delays = [2, 5, 10]  # seconds between retries

            for attempt in range(max_retries):
                try:
                    full_text = ""
                    finish_reason = None
                    for chunk in self.gemini_client.models.generate_content_stream(
                        model=settings.GEMINI_MODEL,
                        contents=contents,
                        config=config,
                    ):
                        if chunk.text:
                            full_text += chunk.text
                        # Capture finish reason from last chunk
                        try:
                            if chunk.candidates and chunk.candidates[0].finish_reason:
                                finish_reason = chunk.candidates[0].finish_reason.name
                        except Exception:
                            pass

                    if not full_text:
                        raise ValueError("Gemini returned an empty response.")

                    # If truncated due to token limit, add a continuation note
                    if finish_reason == "MAX_TOKENS":
                        full_text += (
                            "\n\n---\n> Response was cut off (token limit reached). "
                            "Ask me to continue or request a specific section for the full answer."
                        )
                    return full_text

                except Exception as e:
                    err_str = str(e)
                    is_retryable = any(x in err_str for x in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500"])
                    if is_retryable and attempt < max_retries - 1:
                        wait = retry_delays[attempt]
                        print(f"  ⚠️  Gemini {err_str[:60]}... retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                        time.sleep(wait)
                        continue
                    raise  # re-raise on final attempt or non-retryable error

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _stream)

    async def _call_claude(self, system_prompt: str, messages: list) -> str:
        """Call Claude API as fallback when Gemini quota is exceeded or blocks content."""
        import asyncio
        import anthropic

        api_key = settings.ANTHROPIC_API_KEY
        if not api_key or api_key == "your-anthropic-api-key-here":
            raise ValueError("ANTHROPIC_API_KEY not set in backend/.env")

        client = anthropic.Anthropic(api_key=api_key)

        # Convert messages to Anthropic format
        anthropic_messages = []
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            anthropic_messages.append({"role": role, "content": msg["content"]})

        def _call():
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                system=system_prompt,
                messages=anthropic_messages,
            )
            return response.content[0].text

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _call)

    async def generate_answer(self, query: str, chat_history: list = None) -> dict:
        """Full RAG + MoE pipeline: route -> retrieve -> generate.
        Claude is the primary engine for ALL queries (always respects system prompts).
        Gemini is used only as a fallback when Claude is unavailable.
        """
        expert_id = self.router.route(query)
        expert = EXPERTS[expert_id]

        # RAG retrieval
        retrieved_docs = self.retrieve(query, expert_id)

        context = ""
        if retrieved_docs:
            context = "\n\n## Retrieved Knowledge:\n" + "\n".join(
                f"- {doc['text']}" for doc in retrieved_docs
            )

        # Build message history
        messages = []
        if chat_history:
            for msg in (chat_history or [])[-8:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Build user prompt
        if context:
            user_content = (
                f"VERIFIED FACTS (treat as ground truth for any factual numbers/counts):\n{context}\n\n"
                f"Question: {query}\n\n"
                f"Answer the question in detail, using the verified facts above for any "
                f"specific numbers, counts, or dates. You may add additional helpful "
                f"context from your own knowledge as well."
            )
        else:
            user_content = query
        messages.append({"role": "user", "content": user_content})

        # ── AI engine: Gemini primary, Claude fallback ──────────────────────────
        gemini_key = settings.GEMINI_API_KEY
        claude_key = settings.ANTHROPIC_API_KEY
        gemini_ready = bool(gemini_key and gemini_key not in ("your-gemini-api-key-here", ""))
        claude_ready = bool(claude_key and claude_key not in ("your-anthropic-api-key-here", ""))

        answer = None

        # Try Gemini first (free tier) — with retry on 503/429
        if gemini_ready:
            import asyncio as _asyncio
            retry_delays = [3, 8, 15]
            last_err = None
            for attempt, delay in enumerate([0] + retry_delays):
                if delay:
                    print(f"  ⏳ Gemini 503/429 — waiting {delay}s before retry {attempt}/{len(retry_delays)}...")
                    await _asyncio.sleep(delay)
                try:
                    answer = await self._call_gemini(expert["system_prompt"], messages)
                    last_err = None
                    break  # success
                except Exception as e:
                    err_str = str(e)
                    last_err = e
                    is_retryable = any(x in err_str for x in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"])
                    is_blocked = "SAFETY" in err_str or "blocked" in err_str.lower()
                    if is_retryable and attempt < len(retry_delays):
                        continue  # retry
                    if is_blocked and claude_ready:
                        answer = None
                    elif not claude_ready:
                        kb_section = "\n\n".join(
                            f"**{i+1}.** {d['text']}" for i, d in enumerate(retrieved_docs)
                        ) if retrieved_docs else ""
                        answer = (
                            f"**Gemini error:** {err_str}\n\n"
                            + ("---\n" + kb_section if kb_section else "")
                        )
                    else:
                        answer = None  # fall through to Claude
                    break

            # If all retries exhausted on 503/429 and Claude available, fall through
            if last_err and answer is None and claude_ready:
                print(f"Gemini failed after retries — switching to Claude")

        # Claude fallback
        if answer is None and claude_ready:
            try:
                answer = await self._call_claude(expert["system_prompt"], messages)
            except Exception as e:
                kb_section = "\n\n".join(
                    f"**{i+1}.** {d['text']}" for i, d in enumerate(retrieved_docs)
                ) if retrieved_docs else ""
                answer = (
                    f"**Claude error:** {str(e)}\n\n"
                    + ("---\n" + kb_section if kb_section else "")
                )

        # No keys configured at all
        if answer is None:
            kb_section = "\n\n".join(
                f"**{i+1}.** {d['text']}" for i, d in enumerate(retrieved_docs)
            ) if retrieved_docs else ""
            answer = (
                "**Setup required** — add at least one API key in Render dashboard → Environment:\n\n"
                "**Option A (Free) — Gemini:**\n"
                "`GEMINI_API_KEY` → get free key at https://aistudio.google.com\n\n"
                "**Option B — Claude:**\n"
                "`ANTHROPIC_API_KEY` → get key at https://console.anthropic.com"
                + ("\n\n---\n" + kb_section if kb_section else "")
            )

        sources = [
            {
                "text": d["text"][:180] + ("..." if len(d["text"]) > 180 else ""),
                "score": d["score"],
            }
            for d in retrieved_docs
        ]

        # Fact-check guardrail: if RAG has a verified numeric fact the LLM contradicted, fix it
        if retrieved_docs and answer:
            answer = self._apply_fact_guardrail(query, answer, retrieved_docs)

        return {
            "answer": answer,
            "expert_used": f"{expert['icon']} {expert['name']}",
            "expert_id": expert_id,
            "sources": sources,
        }

    def _apply_fact_guardrail(self, query: str, answer: str, docs: list) -> str:
        """
        If the retrieved docs contain a clear fact that directly answers the query,
        and the LLM answer contradicts it, prepend a correction note with the right answer.
        This prevents small models from hallucinating over verified RAG knowledge.
        """
        import re
        q = query.lower()

        # Known fact patterns: (query keywords, fact regex in doc, canonical answer extract)
        fact_patterns = [
            # bones
            (
                ["how many bones", "number of bones", "bones in human", "bones does a human", "bones in the human", "bones in body"],
                r"adult human body has exactly (\d+) bones",
                "A human adult has **206 bones** in their body. "
                "(Babies are born with ~270 bones that gradually fuse to 206 by adulthood.)"
            ),
            # teeth
            (
                ["how many teeth", "number of teeth", "teeth does a human", "teeth in human"],
                r"adults have (\d+) teeth",
                "An adult human has **32 teeth** (including 4 wisdom teeth)."
            ),
            # muscles
            (
                ["how many muscles", "number of muscles", "muscles in human", "muscles does a human"],
                r"~(\d+)[–-](\d+) skeletal muscles",
                "The human body has approximately **600–650 skeletal muscles**."
            ),
            # heart rate
            (
                ["heart beat", "heart rate", "times heart beats"],
                r"Heart beats ~(\d+)[–-](\d+) times/min",
                "The human heart beats approximately **60–100 times per minute**."
            ),
        ]

        for keywords, doc_pattern, correct_answer in fact_patterns:
            # Check if query matches this fact type
            if not any(kw in q for kw in keywords):
                continue

            # Check if any retrieved doc contains the canonical fact
            doc_has_fact = any(
                re.search(doc_pattern, doc["text"], re.IGNORECASE)
                for doc in docs
            )
            if not doc_has_fact:
                continue

            # Extract the number the LLM gave in its answer
            lm_numbers = re.findall(r'(\d+)', answer)

            # For bones: correct answer is 206 — if LLM didn't say 206, override
            if "bones" in " ".join(keywords):
                if "206" not in answer:
                    correction = "Warning: The model gave an incorrect answer. Verified fact: " + correct_answer
                    return correction

            # For teeth: correct is 32
            elif "teeth" in " ".join(keywords):
                if "32" not in answer:
                    return "Verified fact: " + correct_answer

        return answer


def get_rag_service() -> RAGService:
    return RAGService.get_instance()
