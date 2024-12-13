from crewai_tools import tool
import requests

@tool
def search_recipe(ingredients: str):
    """Useful for searching a recipe using the ingredients."""
    params = {
        "query": ingredients, '''Ingredients given by the user, translate it in english and remove any special charters or number'''
        "sustainabilityWeight": 100,
        "cursor": "",
        "useCfi": 0
    }
    try:
        url = "https://foodprint.matteofusillo.com/recipes-search/by-ingredients"
        # Send a request to the external recipe API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful
        
        # Parse the API response
        response = response.json()
        if response['data']['data'][0]:
            recipe = response['data']['data'][0]
            print(recipe)
            return f"Recipe name: {recipe['title']}, Ingredients list: {recipe['ingredients_list']}"
        else:
            return f"Recipe with this ingredients: '{ingredients}' not found, use your knowledge to resolve the task"

    except requests.exceptions.RequestException as e:
        return f"API request failed: {e}, use your knowledge to resolve the task"