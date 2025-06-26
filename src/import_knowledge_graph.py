#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from typing import Dict, List, Any
from neo4j import GraphDatabase


class KnowledgeGraphImporter:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            self.logger.info("Database cleared")
    
    def create_disease_node(self, session, disease_data: Dict[str, Any]):
        disease_name = disease_data.get("名称", "")
        
        cypher = """
        CREATE (d:Disease {
            name: $name,
            overview: $overview
        })
        RETURN d
        """
        
        session.run(cypher, {
            "name": disease_name,
            "overview": disease_data.get("概述", "")
        })
        
        self.logger.info(f"Created disease node: {disease_name}")
        return disease_name
    
    def create_disease_attribute_nodes(self, session, disease_name: str, disease_data: Dict[str, Any]):
        location = disease_data.get("发病部位", "")
        if location:
            cypher = """
            MERGE (l:Location {name: $location})
            WITH l
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_LOCATION]->(l)
            """
            session.run(cypher, {"location": location, "disease_name": disease_name})
        
        cause = disease_data.get("病因", "")
        if cause:
            cypher = """
            MERGE (c:Cause {description: $cause})
            WITH c
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_CAUSE]->(c)
            """
            session.run(cypher, {"cause": cause, "disease_name": disease_name})
        
        pathology = disease_data.get("病理", "")
        if pathology:
            cypher = """
            MERGE (p:Pathology {description: $pathology})
            WITH p
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_PATHOLOGY]->(p)
            """
            session.run(cypher, {"pathology": pathology, "disease_name": disease_name})
        
        description = disease_data.get("描述特征", "")
        if description:
            cypher = """
            MERGE (desc:Description {text: $description})
            WITH desc
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_DESCRIPTION]->(desc)
            """
            session.run(cypher, {"description": description, "disease_name": disease_name})
        
        anatomical_location = disease_data.get("解剖部位", "")
        if anatomical_location:
            cypher = """
            MERGE (al:AnatomicalLocation {name: $anatomical_location})
            WITH al
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_ANATOMICAL_LOCATION]->(al)
            """
            session.run(cypher, {"anatomical_location": anatomical_location, "disease_name": disease_name})
        
        severity = disease_data.get("程度", "")
        if severity:
            cypher = """
            MERGE (s:Severity {level: $severity})
            WITH s
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_SEVERITY]->(s)
            """
            session.run(cypher, {"severity": severity, "disease_name": disease_name})
        
        duration = disease_data.get("持续时间", "")
        if duration:
            cypher = """
            MERGE (dur:Duration {period: $duration})
            WITH dur
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_DURATION]->(dur)
            """
            session.run(cypher, {"duration": duration, "disease_name": disease_name})
        
        referred_pain = disease_data.get("转移性疼痛", "")
        if referred_pain:
            cypher = """
            MERGE (rp:ReferredPain {description: $referred_pain})
            WITH rp
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_REFERRED_PAIN]->(rp)
            """
            session.run(cypher, {"referred_pain": referred_pain, "disease_name": disease_name})
    
    def create_symptom_nodes(self, session, disease_name: str, clinical_manifestations: Dict[str, List]):
        symptoms = clinical_manifestations.get("症状", [])
        signs = clinical_manifestations.get("体征", [])
        
        for symptom in symptoms:
            cypher = """
            MERGE (s:Symptom {name: $symptom})
            WITH s
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_SYMPTOM]->(s)
            """
            session.run(cypher, {"symptom": symptom, "disease_name": disease_name})
        
        for sign in signs:
            cypher = """
            MERGE (s:Sign {name: $sign})
            WITH s
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_SIGN]->(s)
            """
            session.run(cypher, {"sign": sign, "disease_name": disease_name})
    
    def create_examination_nodes(self, session, disease_name: str, examinations: List[str], indicators: List[str]):
        for exam in examinations:
            cypher = """
            MERGE (e:Examination {name: $exam})
            WITH e
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:REQUIRES_EXAMINATION]->(e)
            """
            session.run(cypher, {"exam": exam, "disease_name": disease_name})
        
        for indicator in indicators:
            cypher = """
            MERGE (i:Indicator {name: $indicator})
            WITH i
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:HAS_INDICATOR]->(i)
            """
            session.run(cypher, {"indicator": indicator, "disease_name": disease_name})
    
    def create_treatment_nodes(self, session, disease_name: str, treatment_data: Dict):
        drug_treatment = treatment_data.get("药物治疗", {})
        non_drug_treatment = treatment_data.get("非药治疗", [])
        surgery = treatment_data.get("手术", [])
        
        if drug_treatment:
            drug_names = drug_treatment.get("药品名称", [])
            frequencies = drug_treatment.get("用药频率", [])
            dosages = drug_treatment.get("用药剂量", [])
            methods = drug_treatment.get("用药方法", [])
            
            for i, drug_name in enumerate(drug_names):
                frequency = frequencies[i] if i < len(frequencies) else ""
                dosage = dosages[i] if i < len(dosages) else ""
                method = methods[i] if i < len(methods) else ""
                
                cypher = """
                MERGE (m:Medication {
                    name: $drug_name,
                    frequency: $frequency,
                    dosage: $dosage,
                    method: $method
                })
                WITH m
                MATCH (d:Disease {name: $disease_name})
                MERGE (d)-[:TREATED_WITH_MEDICATION]->(m)
                """
                session.run(cypher, {
                    "drug_name": drug_name,
                    "frequency": frequency,
                    "dosage": dosage,
                    "method": method,
                    "disease_name": disease_name
                })
        
        for treatment in non_drug_treatment:
            cypher = """
            MERGE (t:NonDrugTreatment {name: $treatment})
            WITH t
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:TREATED_WITH_NON_DRUG]->(t)
            """
            session.run(cypher, {"treatment": treatment, "disease_name": disease_name})
        
        for surgery_type in surgery:
            cypher = """
            MERGE (s:Surgery {name: $surgery_type})
            WITH s
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:TREATED_WITH_SURGERY]->(s)
            """
            session.run(cypher, {"surgery_type": surgery_type, "disease_name": disease_name})
    
    def create_complication_nodes(self, session, disease_name: str, complications: List[str]):
        for complication in complications:
            cypher = """
            MERGE (c:Complication {name: $complication})
            WITH c
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:MAY_CAUSE]->(c)
            """
            session.run(cypher, {"complication": complication, "disease_name": disease_name})
    
    def create_adverse_reaction_nodes(self, session, disease_name: str, adverse_reactions: List[str]):
        for reaction in adverse_reactions:
            cypher = """
            MERGE (a:AdverseReaction {name: $reaction})
            WITH a
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:MAY_HAVE_ADVERSE_REACTION]->(a)
            """
            session.run(cypher, {"reaction": reaction, "disease_name": disease_name})
    
    def create_department_nodes(self, session, disease_name: str, departments: List[str]):
        for department in departments:
            cypher = """
            MERGE (dept:Department {name: $department})
            WITH dept
            MATCH (d:Disease {name: $disease_name})
            MERGE (d)-[:RELATED_TO_DEPARTMENT]->(dept)
            """
            session.run(cypher, {"department": department, "disease_name": disease_name})
    
    def import_disease(self, disease_data: Dict[str, Any]):
        with self.driver.session() as session:
            disease_name = self.create_disease_node(session, disease_data)
            
            self.create_disease_attribute_nodes(session, disease_name, disease_data)
            
            clinical_manifestations = disease_data.get("临床表现", {})
            if clinical_manifestations:
                self.create_symptom_nodes(session, disease_name, clinical_manifestations)
            
            examinations = disease_data.get("检查方法", [])
            indicators = disease_data.get("检查指标值", [])
            if examinations or indicators:
                self.create_examination_nodes(session, disease_name, examinations, indicators)
            
            treatment = disease_data.get("治疗", {})
            if treatment:
                self.create_treatment_nodes(session, disease_name, treatment)
            
            complications = disease_data.get("并发症", [])
            if complications:
                self.create_complication_nodes(session, disease_name, complications)
            
            adverse_reactions = disease_data.get("不良反应", [])
            if adverse_reactions:
                self.create_adverse_reaction_nodes(session, disease_name, adverse_reactions)
            
            departments = disease_data.get("相关科室", [])
            if departments:
                self.create_department_nodes(session, disease_name, departments)
    
    def import_from_json(self, json_file_path: str, clear_db: bool = False):
        if clear_db:
            self.clear_database()
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                diseases_data = json.load(file)
            
            self.logger.info(f"Loaded {len(diseases_data)} diseases from {json_file_path}")
            
            for i, disease_data in enumerate(diseases_data, 1):
                try:
                    self.import_disease(disease_data)
                    self.logger.info(f"Imported disease {i}/{len(diseases_data)}: {disease_data.get('名称', 'Unknown')}")
                except Exception as e:
                    self.logger.error(f"Failed to import disease {i}: {disease_data.get('名称', 'Unknown')} - {str(e)}")
            
            self.logger.info("Knowledge graph import completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to import knowledge graph: {str(e)}")
            raise


def main():
    NEO4J_HOST = "192.168.0.188"
    NEO4J_BOLT_PORT = "37687"
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = "neo4j@gkry"
    
    neo4j_uri = f"bolt://{NEO4J_HOST}:{NEO4J_BOLT_PORT}"
    json_file_path = "../kg/骨科学ks.json"
    
    importer = KnowledgeGraphImporter(neo4j_uri, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    try:
        print("Starting knowledge graph import...")
        print(f"Neo4j URI: {neo4j_uri}")
        print(f"JSON file: {json_file_path}")
        
        clear_db = input("Clear existing database? (y/N): ").lower().strip() == 'y'
        
        importer.import_from_json(json_file_path, clear_db=clear_db)
        print("Import completed successfully!")
        
    except Exception as e:
        print(f"Import failed: {str(e)}")
    finally:
        importer.close()


if __name__ == "__main__":
    main()