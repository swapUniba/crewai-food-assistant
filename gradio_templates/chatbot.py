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


tasksList = [
        {'label': 0, 'description': 'The user request does not fit any of the other descriptions in the list'},
        {'label': 1, 'description': 'Get to know a new recipe that contains a specific element'},
        {'label': 2, 'description': 'Know the carbon footprint of a specific type of food'},
        {'label': 3, 'description': 'Compare two recipes'},
        {'label': 4, 'description': 'Suggest alternative RECIPES that contains preparation details (in italian a recipe is called: RICETTA). Than if an italian talks about "RICETTA" and alternative this is the right one'},
        {'label': 5, 'description': 'Suggest alternative DISH, that contains just little information (in italian a dish is called: PIATTO). Than if an italian talks about "PIATTO" and alternative this is the right one'}
    ]


actual_state = []
last_answer = []
food_info = "0"


def echo(msg, history):

    if actual_state == []:
        actual_state.append("first_interaction")

    if actual_state[-1] == "first_interaction":
        return first_interaction_handler(msg)

    if "second_interaction" in actual_state[-1]:
        return second_interaction_handler(msg)
        


def first_interaction_handler(msg):
    inputs = {'tasks_list': tasksList, 'user_answer': msg}
    result = dispatcher_crew.kickoff(inputs=inputs)

    global food_info
    food_info = food_extractor_crew_config.kickoff(inputs={'user_answer': msg})

    if "0" in result:
        actual_state.append("first_interaction")
        last_answer.append("Mi dispiace ma non sono ancora in grado di rispondere a questa richiesta")

    if "1" in result:
        actual_state.append("second_interaction_1")
        if "0" in food_info:
            last_answer.append("Dimmi almeno un ingrediente che ti piacerebbe trovare all'interno della ricetta")

    if "2" in result:
        actual_state.append("second_interaction_2")
        if "0" in food_info:
            last_answer.append("Scrivimi il nome della ricetta ed eventuali ingredienti aggiuntivi")

    if "3" in result:
        actual_state.append("second_interaction_3")
        if "0" in food_info:
            last_answer.append("Dammi il nome o alcune informazioni sulle ricette che vorresti confrontare")

    if "4" in result:
        actual_state.append("second_interaction_4")
        if "0" in food_info:
            last_answer.append("Scrivimi il nome o qualche informazione sulla ricetta della quale vorresti conoscere un'alternativa")

    if "5" in result:
        actual_state.append("second_interaction_5")
        if "0" in food_info:
            last_answer.append("Scrivimi il nome o qualche informazione sul piatto del quale vorresti conoscere un'alternativa")

    if "0" in food_info: 
        return last_answer[-1]
    
    return second_interaction_handler(msg)
    


def second_interaction_handler(msg):   

    global food_info
    if "0" in food_info: 
        isValidAnswer = answer_validation_crew.kickoff(inputs={'question_done': last_answer, 'user_answer': msg})
    else:
        isValidAnswer = "1"
        msg = food_info


    if "1" not in isValidAnswer:
        last_answer.append(isValidAnswer)
        return last_answer[-1]

    if "1" in actual_state[-1]:
        last_answer.append(recipes_searcher_crew.kickoff(inputs={'ingredients': msg}))

    if "2" in actual_state[-1]:
        last_answer.append(recipes_carbon_footprint_checker_crew.kickoff(inputs={'recipe': msg}))

    if "3" in actual_state[-1]:
        last_answer.append(recipes_health_comparison_crew.kickoff(inputs={'recipes': msg}))

    if "4" in actual_state[-1]:
        last_answer.append(recipes_alternative_crew.kickoff(inputs={'recipe': msg}))

    if "5" in actual_state[-1]:
        last_answer.append(dish_alternative_crew.kickoff(inputs={'dish': msg}))
    
    actual_state.append("first_interaction")
    food_info = ""
    return last_answer[-1]



demo = gr.ChatInterface(
    fn=echo,
    examples=[
        "Mi dici una nuova ricetta?", 
        "Vorrei sapere quanto inquina una ricetta",
        "Fai un confronto tra due ricette",
        "Suggeriscimi una ricetta alternativa"
    ],
    title="Recipes Crew",
)

demo.launch(share=True)