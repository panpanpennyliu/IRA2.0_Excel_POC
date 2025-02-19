PLAN_FORMAT = """
Based on background and knowledge given above to generate a plan, put each step in the json format as the output, step has attribute step_name, step_description, model_name and process_type. Copy step descriptions from knowledge directly to step_description without any change, including examples and details. All steps are under 'steps' root attribute.
ex: step_name: Prepare eggs, step_description: Get the eggs from the fridge and put on the table, model_name: gpt-4o-mini, process_type: text.
"""