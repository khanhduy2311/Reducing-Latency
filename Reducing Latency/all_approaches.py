import asyncio
import re
import concurrent.futures
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model

""" This is a demonstration for using asynchronous multi-threading with WatsonX AI. Several approaches have been tried out here. """

def all_approaches(async_mode):

    # Select Model for your use-case

    model = "meta-llama/llama-2-70b-chat"

    my_credentials = {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": "ADD YOUR KEYS"
    }

    model_id = ModelTypes.LLAMA_2_70B_CHAT
    gen_parms = {"decoding_method": "greedy", "min_new_tokens": 10, "max_new_tokens": 250, "random_seed": 1024}
    project_id = "ADD YOUR PROJECT ID"
    space_id = None
    verify = False

    model = Model(model_id, my_credentials, gen_parms, project_id, space_id, verify)

    prompt_1 = """ TASK 1 Prompt """
    prompt_2 = """ TASK 2 Prompt """
    prompt_3 = """ TASK 3 Prompt """
    prompt_4 = """ TASK 4 Prompt """

    prompts = {"Task1": prompt_1,
               "Task2": prompt_2,
               "Task3": prompt_3,
               "Task4": prompt_4
               }

    gen_parms_override = None

    if async_mode == "original":

        results = {}
        for k in prompts:
            generated_response = model.generate(prompts[k], gen_parms_override)
            response = generated_response['results'][0]['generated_text']
            results[k] = '\n'.join([line.strip() for line in response.split('\n') if line.strip()])

        return results

    # this method returns answers in unordered concat form and is difficult in processing to the required format. Not preffered.
    elif async_mode == "inbuilt_async":
        results = {}
        prompt_list = [x for x in list(prompts.values())]
        generated_response = model.generate(prompt_list, gen_parms, async_mode=True, concurrency_limit=10, )
        for list_num, (k, result) in enumerate(zip(prompts.keys(), list(generated_response))):
            pattern = re.compile(r'<s>\[INST\] <<SYS>>.*?\[/INST\]', re.DOTALL)
            response = result['results'][0]['generated_text']
            response = re.sub(pattern, '', response)
            results[k] = '\n'.join([line.strip() for line in response.split('\n') if line.strip()])

        return results

    elif async_mode == "concurrent_futures":
        results = {}

        def multiple_api_calls(k):
            generated_response = model.generate(prompts[k], gen_parms_override)
            response = generated_response['results'][0]['generated_text']
            results[k] = '\n'.join([line.strip() for line in response.split('\n') if line.strip()])
            return results

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(multiple_api_calls, prompts.keys()))[0]
            results = {'Task1': results.get('Task1'), 'Task2': results.get('Task2'),
                               'Task3': results.get('Task3'), 'Task4': results.get('Task4')}
            return results

    elif async_mode == "asyncio":

        async def generate_response(model, prompt, gen_parms_override):
            def get_response():
                generated_response = model.generate(prompt, gen_parms_override)
                response = generated_response['results'][0]['generated_text']
                formatted_responss = '\n'.join([line.strip() for line in response.split('\n') if line.strip()])
                return formatted_responss

            return await asyncio.to_thread(get_response)

        async def handle_prompts_async(model, prompts, gen_parms_override):
            tasks = []
            for prompt_key, prompt_template in prompts.items():
                prompt = prompt_template
                task = generate_response(model, prompt, gen_parms_override)
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            return {prompt_key: response for prompt_key, response in zip(prompts.keys(), responses)}

        async def main():
            results = await handle_prompts_async(model, prompts, gen_parms_override)
            return results

        results = asyncio.run(main())

    return results