import gradio as gr
import os
from dotenv import load_dotenv
load_dotenv()

from recipes_crew.crew import dispatcher_crew
from recipes_crew.crew import recipes_searcher_crew
from recipes_crew.crew import recipes_carbon_footprint_checker_crew
from recipes_crew.crew import recipes_health_comparison_crew
from recipes_crew.crew import recipes_alternative_crew
from recipes_crew.crew import answer_validation_crew
from recipes_crew.crew import food_extractor_crew_config
from recipes_crew.crew import dish_alternative_crew
from recipes_crew.crew import conversation_context_linker_crew

tasksList = [
    {'label': 0, 'description': 'The user request does not fit any of the other descriptions in the list'},
    {'label': 1, 'description': 'Get to know a new recipe that contains a specific element, if you find the word NUOVA, maybe is this task'},
    {'label': 2, 'description': 'Know the carbon footprint of a specific type of food'},
    {'label': 3, 'description': 'Compare two recipes'},
    {'label': 4, 'description': 'Suggest alternative RECIPES that contains preparation details (in italian a recipe is called: RICETTA). Than if an italian talks about "RICETTA" and alternative this is the right one'},
    {'label': 5, 'description': 'Suggest alternative DISH, that contains just little information (in italian a dish is called: PIATTO). Than if an italian talks about "PIATTO" and "ALTERNATIVE" this is the right one'}
]

def echo(user_message, history, actual_state, last_answer, food_info, user_preferences):
    if actual_state is None or actual_state == []:
        actual_state = []

    # If user_preferences is not set, start the user preferences collection
    if not user_preferences:
        if 'awaiting_user_preferences' not in actual_state and 'collecting_user_preferences' not in actual_state:
            actual_state.append('awaiting_user_preferences')

    if actual_state[-1] == 'awaiting_user_preferences':
        # Bot sends the initial message
        response = "Ciao, raccontami di più su di te, quali ingredienti ami? Hai intolleranze, allergie?"
        history[-1][1] = response
        # Update actual_state
        actual_state.append('collecting_user_preferences')
        return history, actual_state, last_answer, food_info, user_preferences

    elif actual_state[-1] == 'collecting_user_preferences':
        # Save user response as user_preferences
        user_preferences = user_message
        # Update state
        last_answer.append("Grazie per aver condiviso le tue preferenze. Adesso puoi chiedermi qualcosa!")
        actual_state.append('first_interaction')
        history[-1][1] = last_answer[-1]
        return history, actual_state, last_answer, food_info, user_preferences

    elif actual_state[-1] == "first_interaction":
        response, actual_state, last_answer, food_info = first_interaction_handler(user_message, actual_state, last_answer, food_info)
        history[-1][1] = response  # Update assistant's response
        return history, actual_state, last_answer, food_info, user_preferences

    elif "second_interaction" in actual_state[-1]:
        response, actual_state, last_answer, food_info = second_interaction_handler(user_message, actual_state, last_answer, food_info, user_preferences)
        history[-1][1] = response  # Update assistant's response
        return history, actual_state, last_answer, food_info, user_preferences

    else:
        # Default response if state is somehow invalid
        history[-1][1] = "Qualcosa è andato storto. Per favore, riprova."
        return history, actual_state, last_answer, food_info, user_preferences

def first_interaction_handler(msg, actual_state, last_answer, food_info):
    inputs = {'tasks_list': tasksList, 'user_answer': msg}
    result = dispatcher_crew.kickoff(inputs=inputs)

    food_info = food_extractor_crew_config.kickoff(inputs={'user_answer': msg})

    if "0" in result:
        actual_state.append("first_interaction")
        last_answer.append("Mi dispiace ma non sono ancora in grado di rispondere a questa richiesta")
        return last_answer[-1], actual_state, last_answer, food_info

    if "1" in result:
        actual_state.append("second_interaction_1")
        if "0" in food_info:
            last_answer.append("Dimmi almeno un ingrediente che ti piacerebbe trovare all'interno della ricetta")
            return last_answer[-1], actual_state, last_answer, food_info

    if "2" in result:
        actual_state.append("second_interaction_2")
        if "0" in food_info:
            last_answer.append("Scrivimi il nome della ricetta ed eventuali ingredienti aggiuntivi")
            return last_answer[-1], actual_state, last_answer, food_info

    if "3" in result:
        actual_state.append("second_interaction_3")
        if "0" in food_info:
            last_answer.append("Dammi il nome o alcune informazioni sulle ricette che vorresti confrontare")
            return last_answer[-1], actual_state, last_answer, food_info

    if "4" in result:
        actual_state.append("second_interaction_4")
        if "0" in food_info:
            last_answer.append("Scrivimi il nome o qualche informazione sulla ricetta della quale vorresti conoscere un'alternativa")
            return last_answer[-1], actual_state, last_answer, food_info

    if "5" in result:
        actual_state.append("second_interaction_5")
        if "0" in food_info:
            last_answer.append("Scrivimi il nome o qualche informazione sul piatto del quale vorresti conoscere le alternative")
            return last_answer[-1], actual_state, last_answer, food_info


    if "0" in food_info:
        return last_answer[-1], actual_state, last_answer, food_info

    # If food_info is already available, proceed to second interaction
    return second_interaction_handler(msg, actual_state, last_answer, food_info, '')

def second_interaction_handler(msg, actual_state, last_answer, food_info, user_preferences):
    if "0" in food_info:
        isValidAnswer = answer_validation_crew.kickoff(inputs={'question_done': last_answer[-1], 'user_answer': msg})
    else:
        isValidAnswer = "1"
        msg = food_info

    if "1" not in isValidAnswer:
        last_answer.append(isValidAnswer)
        return last_answer[-1], actual_state, last_answer, food_info

    if "1" in actual_state[-1]:
        last_answer.append(recipes_searcher_crew.kickoff(inputs={'ingredients': msg, 'user_preferences': user_preferences}))

    if "2" in actual_state[-1]:
        last_answer.append(recipes_carbon_footprint_checker_crew.kickoff(inputs={'recipe': msg, 'user_preferences': user_preferences}))

    if "3" in actual_state[-1]:
        last_answer.append(recipes_health_comparison_crew.kickoff(inputs={'recipes': msg, 'user_preferences': user_preferences}))

    if "4" in actual_state[-1]:
        last_answer.append(recipes_alternative_crew.kickoff(inputs={'recipe': msg, 'user_preferences': user_preferences}))

    if "5" in actual_state[-1]:
        last_answer.append(dish_alternative_crew.kickoff(inputs={'dish': msg, 'user_preferences': user_preferences}))


    actual_state.append("first_interaction")
    food_info = ""
    return last_answer[-1], actual_state, last_answer, food_info


with gr.Blocks(
    css="""
        #conversation-container {
            min-height: 500px;
        }

        #description-text {
            text-align: center;
            font-size: 14px;
            margin-bottom: 0px;
        }

        #header {
            text-align: center;
            margin-bottom: 10px;
        }

        #header img {
            max-width: 100%;
            height: auto;
        }
        """
) as demo:
    # Added image at the top instead of the title
    with gr.Column(elem_id="header"):
        # Replace 'gradio_templates/img/cooking_crew_logo.png' with the actual path or URL of your image
        gr.Image("gradio_templates/img/cooking_crew_logo.png", elem_id="bot-image", show_label=False, interactive=False, height=200, container=False)
        description_text = gr.Markdown(
            "<div id='description-text'>"
                "Hai mai avuto una crew di chef al tuo servizio?<br/>"
                "Saluta il chatbot, rispondi alle sue domande e immergiti in un’esperienza culinaria unica, ricca di sapori, consigli e ispirazioni per diventare un vero maestro ai fornelli.<br>"
                "Quando avrai finito <a href=\"https://docs.google.com/forms/d/e/1FAIpQLScuCgqihsW9xv_uRoyJdqwZQCVqPtMhCfmsZ6x8UYOOGvuZWg/viewform\">clicca qui</a> per rispondere alle domande finali!"
            "</div>",
            elem_id="description-text",
            visible=False  # Hide the description text initially
        )

    # Initial text and button
    initial_text = gr.Markdown(
        "<div style='font-size:20px'>"
            "Ciao, ti diamo il benvenut@ in questo esperimento!<br>"
            "Per prima cosa vogliamo ringraziarti per aver accettato di provare questo assistente virtuale, il tuo contributo sarà essenziale per comprendere al meglio come realizzare assistenti digitali che portino un valore aggiunto nella nostra società!<br><br>"
            "Prima di iniziare ti chiedo di compilare il questionario per le informazioni anagrafiche e di preparazione che <a href=\"https://docs.google.com/forms/d/e/1FAIpQLSeGz8T5yfss2i9gzH2rH2NpQSnWAEuhO7xKwBA2yAhM7pwT5A/viewform\">trovi qui.</a><br><br>"
            "Stai per entrare in contatto con la <b>Coocking Crew</b> una crew dotata di intelligenza artificiale il cui compito è essere un supporto nelle tue scelte alimentari, con particolare attenzione al tema della sostenibilità e all'impatto ambientale delle ricette che prepariamo.<br>"
            "Una avviata la conversazione, rispondi alle domande poste dalla coocking crew per avere una esperienza completamente personalizzata.<br><br>"
            "Ai fini della riuscita dell'esperimento è necessario che tu faccia compiere alla coocking crew almeno una volta TUTTE le seguenti azioni:<br>"
            "- Trovare una ricetta in base al nome o lista di ingredienti<br>"
            "- Fare domande su una ricetta trovata (ad es. \"X è una ricetta sostenibile?\" oppure \"Y è una ricetta salutare?\" oppure \"Z è una ricetta adatta a me?\")<br>"
            "- Trovare una ricetta sostenibile alternativa rispetto a una già cercata o che indicherai tu<br>"  
            "- Confrontare due ricette dal punto di vista della sostenibilità<br>"
            "Per ricordare tutti i task da compiere, puoi utilizzare gli esempi qui in basso che rimarranno disponibili durante l'esperimento!<br><br>"
            "Clicca <b>Avanti</b> ed inizia a divertirti!"
        "</div>"
        )
    start_button = gr.Button("Inizia")

    # Chatbot components, initially hidden
    state = gr.State({
        'actual_state': [],
        'last_answer': [],
        'food_info': "0",
        'user_preferences': ''
    })

    chatbot = gr.Chatbot(visible=False, elem_id="conversation-container")
    
    msg = gr.Textbox(
        show_label=False,
        placeholder="Scrivi qui il tuo messaggio...",
        visible=False
    ).style(container=False)
    send_button = gr.Button("Send", visible=False)

    def start_chat():
        return [
            gr.update(visible=False),  # Hide initial_text
            gr.update(visible=False),  # Hide start_button
            gr.update(visible=True),   # Show description_text
            gr.update(visible=True),   # Show chatbot
            gr.update(visible=True, value='Ciao'),   # Show msg input with 'Ciao' pre-filled
            gr.update(visible=True)    # Show send_button
        ]

    start_button.click(
        start_chat,
        inputs=[],
        outputs=[initial_text, start_button, description_text, chatbot, msg, send_button]
    )

    def user_message(user_message, history):
        history = history + [[user_message, None]]
        return "", history  # Clear input box and update history

    def bot_response(history, state, request: gr.Request):
        actual_state = state['actual_state']
        last_answer = state['last_answer']
        food_info = state['food_info']
        user_preferences = state.get('user_preferences', '')

        # Load user preferences if not already in state
        token = request.query_params.get('token')
        if token and not user_preferences:
            preferences_path = os.path.join('conversations', token, 'user_preferences.txt')
            if os.path.exists(preferences_path):
                with open(preferences_path, 'r', encoding='utf-8') as f:
                    user_preferences = f.read()
                    state['user_preferences'] = user_preferences

        user_message = history[-1][0]

        # Process assistant's response
        history, actual_state, last_answer, food_info, user_preferences = echo(
            user_message, history, actual_state, last_answer, food_info, user_preferences
        )

        state['actual_state'] = actual_state
        state['last_answer'] = last_answer
        state['food_info'] = food_info
        state['user_preferences'] = user_preferences

        # Save user_preferences if just collected
        if token and user_preferences:
            # Create the folder if it doesn't exist
            folder_path = os.path.join('conversations', token)
            os.makedirs(folder_path, exist_ok=True)
            # Save the user preferences to 'user_preferences.txt'
            preferences_path = os.path.join(folder_path, 'user_preferences.txt')
            with open(preferences_path, 'w', encoding='utf-8') as f:
                f.write(user_preferences)

        # Save conversation to a folder named after the token in the URL
        if token:
            # Create the folder with the token name inside 'conversations'
            folder_path = os.path.join('conversations', token)
            os.makedirs(folder_path, exist_ok=True)

            # Save conversation to 'conversation.txt' inside the folder
            conversation_path = os.path.join(folder_path, 'conversation.txt')
            with open(conversation_path, 'w', encoding='utf-8') as f:
                for message in history:
                    f.write(f"User: {message[0]}\n")
                    f.write(f"Assistant: {message[1]}\n\n")

        return history, state

    send_button.click(
        fn=user_message,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
    ).then(
        fn=bot_response,
        inputs=[chatbot, state],
        outputs=[chatbot, state],
    )

    msg.submit(
        fn=user_message,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
    ).then(
        fn=bot_response,
        inputs=[chatbot, state],
        outputs=[chatbot, state],
    )

    gr.Examples(
        examples=[
            "Mi dici una nuova ricetta?",
            "Vorrei conoscere una nuova ricetta che contiene i fagioli.",
            "Vorrei sapere quanto inquina una ricetta",
            "Vorrei sapere l'inquinamento prodotto da una tagliata di manzo",
            "Fai un confronto tra due ricette",
            "Confronta la pasta e fagioli e la tagliata di manzo.",
            "Suggeriscimi una ricetta alternativa",
            "Vorrei conoscere un'alternativa alla ricetta per la tagliata di manzo cotta al sangue, con rucola e grana",
            "Vorrei conoscere qualche alternativa da un piatto.",
            "Vorrei conoscere un piatto alternativo alla tagliata di manzo."
        ],
        inputs=msg,
        elem_id="examples"
    )

demo.launch(share=True)