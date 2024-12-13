import os
from dotenv import load_dotenv
load_dotenv()

from recipes_crew.crew import dispatcher_crew
from recipes_crew.crew import recipes_searcher_crew
from recipes_crew.crew import recipes_carbon_footprint_checker_crew
from recipes_crew.crew import recipes_health_comparison_crew
from recipes_crew.crew import recipes_alternative_crew
from recipes_crew.crew import answer_validation_crew
from recipes_crew.crew import answer_validation_crew
from recipes_crew.crew import food_extractor_crew_config
from recipes_crew.crew import conversation_food_extractor_crew
from recipes_crew.crew import dish_alternative_crew

def run():

    # Now 'content' contains the entire contents of the file as a string
    inputs = {'dish': 'pane e pomodoro', 'user_preferences': ''}
    result = dish_alternative_crew.kickoff(inputs=inputs)

    print(result)

    '''
    tasksList = [
        {'label': 1, 'description': 'Get to know a new recipe that contains a specific element'},
        {'label': 2, 'description': 'Know the carbon footprint of a specific type of food'},
        {'label': 3, 'description': 'Compare two recipes'},
        {'label': 4, 'description': 'Suggest alternative recipes'}
    ]

    inputs = {'tasks_list': tasksList, 'user_answer': userTask}
    result = dispatcher_crew.kickoff(inputs=inputs)

    if "1" in result:
        ingredients = food_extractor_crew_config.kickoff(inputs={'user_answer': userTask})
        if "0" in ingredients:
            ingredients = input("Dimmi qualche ingrediente che ti piacerebbe\n")

        print("Risultato:", recipes_searcher_crew.kickoff(inputs={'ingredients': ingredients}))

    if "2" in result:
        recipe = input("Scrivi il nome della ricetta ed eventuali ingredienti aggiuntivi\n")
        print("Risultato:", recipes_carbon_footprint_checker_crew.kickoff(inputs={'recipe': recipe}))

    if "3" in result:
        recipes = input("Dimmi il nome delle ricette da confrontare\n")
        print("Risultato:", recipes_health_comparison_crew.kickoff(inputs={'recipes': recipes}))

    if "4" in result:
        recipe = input("Dimmi il nome della ricetta della quale vorresti una alternativa\n")
        print("Risultato:", recipes_alternative_crew.kickoff(inputs={'recipe': recipe}))'''



if __name__ == '__main__':
    run()