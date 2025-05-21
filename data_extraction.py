import sys
from data_extract.concept_analyzer import ConceptAnalyzer
from data_extract.logic_identifier import LogicIdentifier
from data_extract.knowledge_generator import KnowledgeGenerator
from utils.logger_setup_data_extraction import logger


def run():
    logger.info(f"started...")    
    
    # Step1: Generate concept data
    logger.info(f"\nstarted ConceptAnalyzer...")       
    concept_analyzer = ConceptAnalyzer()
    concept_data = concept_analyzer.generate_concept_data()
    logger.info(f"end ConceptAnalyzer...\n")

    #TODO
    sys.exit(0)

    # Step2: Merge same steps and compound steps
    logger.info(f"\nstarted LogicIdentifier...") 
    logic_identifier = LogicIdentifier(config)
    pattern_data = logic_identifier.merge_steps(concept_data)
    print("Pattern Data:", pattern_data)
    logger.info(f"end LogicIdentifier...\n") 

    # Step3: Generate knowledge JOSN
    logger.info(f"\nstarted KnowledgeGenerator...") 
    knowledge_generator = KnowledgeGenerator(config)
    knowledge_json = knowledge_generator.generate_knowledge_json(pattern_data)
    print("Knowledge JSON:", knowledge_json)
    logger.info(f"started KnowledgeGenerator...\n") 

    logger.info(f"end...") 


if __name__ == "__main__":
    run()