import streamlit as st
from settings import CLAUDE_API_KEY
from example_article import EXAMPLE_ARTICLE

SYSTEM_PROMPT = """
Du är en copy-writer. Ditt uppdrag är att förkorta och omformulera ("rewrita") nyhetstexter som om de var skrivna av TT.  

Det är viktigt:
- Att den nya texten är **exakt** så många tecken som efterfrågats.
- Att information och fakta inte förändras. 
- Att citat återges ordagrannt och oförändrat (däremot får de förkortas).
- [rewrite-instruktion]
- Att den förkortade texten har en rubrik.
- Att texten formatteras i markdown.

Följ även följande skrivregel:
- Procent skrivs ut i procenttal: 
    Rätt: "5 procent".
    Fel: "5%" 
- Citat inleds med –: 
    Rätt: – Lorem ipsus... 
    Fel: "Lorem ipsum..."
- Skriv ut förkortningar:
    Rätt: "till exempel"
    Fel: "t.ex."
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate



#CLAUDE_MODEL = "claude-3-opus-20240229"
#CLAUDE_MODEL = "claude-3-sonnet-20240229"
MODELS = [
    (
        "claude-3-opus-20240229",
        "Our most powerful model, delivering state-of-the-art performance on highly complex tasks and demonstrating fluency and human-like understanding"
    ),
    (
        "claude-3-sonnet-20240229",
        "Our most balanced model between intelligence and speed, a great choice for enterprise workloads and scaled AI deployments"
    ),
    (
        "claude-3-haiku-20240307",
        "Our fastest and most compact model, designed for near-instant responsiveness and seamless AI experiences that mimic human interactions"
    ),
]

# Funktion för att anropa LLM API
def call_llm_api(input_article, n_chars, system_prompt, model, temperature=0, rewrite=True):
    print(f"Call {model}")
    if rewrite:
        rewrite_instrux = "Att brödtexten formuleras med andra ord än originalet (för att undvika plagiarism), men bibehåller sin mening."
    else:
        rewrite_instrux = "Att undvika att omformulera brödtexten."

    system_prompt = system_prompt.replace("[rewrite-instruktion]", rewrite_instrux)
    chat = ChatAnthropic(temperature=temperature, 
                         model_name=model, 
                         anthropic_api_key=CLAUDE_API_KEY)

    human = """
    Förkorta följande text till **{n_chars} tecken**.

    ================

    {input_article}

    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human)
    ])

    chain = prompt | chat
    r = chain.invoke(
        {
            "n_chars": n_chars,
            "input_article": input_article,
        }
    )
    return r.content



# Skapa Streamlit användargränssnitt
st.title("Newsworthy Rewrite (beta)")
st.write("Det här är ett verktyg för att förkorta och skriva om artiklar med hjälp av AI. ")

# Formulär
with st.form("llm_form"):
    input_article = st.text_area("Artikel:", placeholder="Klistra in din artikel här", height=300, value="")
    n_chars = st.number_input("Antal tecken:", min_value=0, value=800)
    rewrite = st.checkbox("Uppmuntra rewrite")

    with st.expander("Avancerade inställningar"):
        # Använda modellnamnen som labels och beskrivningarna som tooltips
        model_choice = st.radio(
            "Choose a model:",
            options=[model[0] for model in MODELS],  # Hämta bara modellnamnen
            format_func=lambda x: f"{' '.join(x.split('-')[:3]).capitalize()}",  # Formatera visningen av modellnamn
            help="Select a model based on your requirement",
        )

        # Visa den valda modellens beskrivning
        temperature = st.number_input("Temperatur:", min_value=0.0, max_value=1.0, value=0.2, step=0.1, format="%.2f")

    #with st.expander("System prompt"):
    #    system_prompt = st.text_area("", value=SYSTEM_PROMPT, placeholder="Enter system prompt here...", height=300)

    submit_button = st.form_submit_button("Rewrita")


    if submit_button:
        with st.spinner('Genererar text...'):
            try:
                # Anropar LLM API när användaren skickar formuläret
                rewritten_article = call_llm_api(input_article=input_article,
                                        n_chars=n_chars,
                                        system_prompt=SYSTEM_PROMPT, 
                                        temperature=temperature,
                                        model=model_choice,
                                        rewrite=rewrite)

                st.write(rewritten_article)
                st.info(f"Antal tecken: {len(rewritten_article)}")
                st.markdown("*Korrekturläs alltid texten. Modellen kan hallucinera. Newsworthy ansvarar inte för eventuella fel.*",)
            except Exception as e:
                st.error(f"Nåt gick fel: {str(e)}")