from typing import Dict, List, Union, Any

from ..driver.neo4j import Neo4jDatabase
from ..llm.basellm import BaseLLM
from .base_component import BaseComponent
import re


class Text2Cypher(BaseComponent):
    def __init__(
        self, llm: BaseLLM, database: Neo4jDatabase, schema: bool, cypher_examples: str
    ) -> None:
        self.llm = llm
        self.database = database
        self.cypher_examples = cypher_examples
        if schema:
            self.schema = database.schema

    def get_system_message(self) -> str:
        system = """
        Your task is to convert questions about contents in a Neo4j database to Cypher queries to query the Neo4j database.
        Use only the provided relationship types and properties.
        Do not use any other relationship types or properties that are not provided.
        """
        if self.schema:
            system += f"""
            If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
            Schema:
            {self.schema}
            """
        if self.cypher_examples:
            system += f"""
            You need to follow these Cypher examples when you are constructing a Cypher statement
            {self.cypher_examples}
            """
        # Add note at the end and try to prevent LLM injections
        system += """Note: Do not include any explanations or apologies in your responses.
                     Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
                     Do not include any text except the generated Cypher statement. This is very important if you want to get paid.
                     Always provide enough context for an LLM to be able to generate valid response.
                     Please wrap the generated Cypher statement in triple backticks (`).
                     """
        return system

    def construct_cypher(self, question: str, history=[]) -> str:
        messages = [{"role": "system", "content": self.get_system_message()}]
        messages.extend(history)
        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )
        print(messages)
        cypher = self.llm.generate(messages)
        return cypher

    def run(
        self, question: str, history: List = [], heal_cypher:bool = True
    ) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        # Add prefix if not part of self-heal loop
        final_question = "Question to be converted to Cypher: " + question if heal_cypher else question
        cypher = self.construct_cypher(final_question, history)
        # finds the first string wrapped in triple backticks. Where the match include the backticks and the first group in the match is the cypher
        match = re.search("```([\w\W]*?)```", cypher)

        # If the LLM didn't any Cypher statement (error, missing context, etc..)
        if match is None:
            return {"output": [{"message": cypher}], "generated_cypher": None}
        extracted_cypher = match.group(1)
        print(f"Generated cypher: {extracted_cypher}")
        
        output = self.database.query(extracted_cypher)
        # Catch Cypher syntax error
        if heal_cypher and output and output[0].get('code') == 'invalid_cypher':
            syntax_messages = [{"role": "system", "content": self.get_system_message()}]
            syntax_messages.extend([{'role': 'user', 'content': question}, {'role':'assistant', 'content': cypher}])
            # Try to heal Cypher syntax only once
            return self.run(output[0].get('message'), syntax_messages, heal_cypher=False)
        
        return {
            "output": output,
            "generated_cypher": extracted_cypher,
        }
