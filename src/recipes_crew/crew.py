import yaml
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_groq import ChatGroq
from recipes_crew.tools.search_recipe import search_recipe
import requests
import os


llm = ChatGroq(model_name="mixtral-8x7b-32768")


def load_yaml(file_path):
    # Construct the absolute path
    base_dir = os.path.dirname(__file__)  # Gets the directory where the script is located
    abs_file_path = os.path.join(base_dir, file_path)

    with open(abs_file_path, 'r') as file:
        return yaml.safe_load(file)




def create_agent(agent_config, tools=[]):
    return Agent(
        role=agent_config['role'],
        goal=agent_config['goal'],
        backstory=agent_config['backstory'],
        tools=tools,
        llm=llm,
        allow_delegation=False,
        verbose=False
    )

def create_task(task_config, agent, tools=[]):
    return Task(
        description=task_config['description'],
        expected_output=task_config['expected_output'],
        agent=agent,
        tools=tools,
        llm=llm
    )

def create_crew(crew_config, agents, tasks):
    
    # Create agent objects
    agents_objs = [create_agent(agents[agent['id']]) for agent in crew_config['agents']]
    
    # Assign tasks to agents sequentially
    tasks_objs = []
    for idx, task in enumerate(crew_config['tasks']):
        agent_idx = idx % len(agents_objs)  # This ensures tasks are assigned in a round-robin manner if there are more tasks than agents
        
        if 'tools' in task:
            tools_obj = [tool_dict[tool['id']] for tool in task['tools']]
        else:
            tools_obj = []

        tasks_objs.append(create_task(tasks[task['id']], agents_objs[agent_idx], tools_obj))
    
    return Crew(
        agents=agents_objs,
        tasks=tasks_objs,
        process=Process.sequential,
        verbose=2
    )

    

tool_dict = {
    "search_recipe": search_recipe
}

agents = load_yaml('config/agents.yaml')
tasks = load_yaml('config/tasks.yaml')

dispatcher_crew_config = load_yaml('config/dispatcherCrew.yaml')['crew']
food_extractor_crew_config = load_yaml('config/foodExtractorCrew.yaml')['crew']
conversation_food_extractor_crew_config = load_yaml('config/conversationFoodExtractorCrew.yaml')['crew']
recipes_searcher_crew_config = load_yaml('config/recipesSearcherCrew.yaml')['crew']
recipes_carbon_footprint_checker_crew_config = load_yaml('config/recipesCarbonFootprintCheckerCrew.yaml')['crew'] 
recipes_health_comparison_crew_config = load_yaml('config/recipesHealthComparisonCrew.yaml')['crew'] 
recipes_alternative_crew_config = load_yaml('config/recipesAlternativeCrew.yaml')['crew'] 
answer_validation_crew_config = load_yaml('config/answerValidationCrew.yaml')['crew'] 
dish_alternative_crew_config = load_yaml('config/dishAlternativeCrew.yaml')['crew'] 
conversation_context_linker_crew_config = load_yaml('config/conversationContextLinkerCrew.yaml')['crew'] 

dispatcher_crew = create_crew(dispatcher_crew_config, agents, tasks)
food_extractor_crew_config = create_crew(food_extractor_crew_config, agents, tasks)
conversation_food_extractor_crew = create_crew(conversation_food_extractor_crew_config, agents, tasks)
recipes_searcher_crew = create_crew(recipes_searcher_crew_config, agents, tasks)
recipes_carbon_footprint_checker_crew = create_crew(recipes_carbon_footprint_checker_crew_config, agents, tasks)  
recipes_health_comparison_crew = create_crew(recipes_health_comparison_crew_config, agents, tasks)  
recipes_alternative_crew = create_crew(recipes_alternative_crew_config, agents, tasks) 
dish_alternative_crew = create_crew(dish_alternative_crew_config, agents, tasks)  
answer_validation_crew = create_crew(answer_validation_crew_config, agents, tasks)
conversation_context_linker_crew = create_crew(conversation_context_linker_crew_config, agents, tasks)