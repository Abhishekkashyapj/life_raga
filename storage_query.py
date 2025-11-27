"""Query both Vector DB and Graph DB with injected data"""

import asyncio
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()


async def query_vector_db():
    """Query the Vector Database (NanoVectorDB)"""
    print("\n" + "="*70)
    print("VECTOR DATABASE QUERIES (NanoVectorDB)")
    print("="*70 + "\n")
    
    try:
        from lightrag.utils import EmbeddingFunc
        from lightrag.llm.ollama import ollama_embed
        
        # Initialize embedding function
        embedding_func = EmbeddingFunc(768, lambda t: ollama_embed(
            t, os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text')
        ))
        
        # Load vector database
        with open('./rag_local/vdb_chunks.json', 'r') as f:
            vectors = json.load(f)
        
        print(f"Vector DB Statistics:")
        print(f"  Total embeddings: {len(vectors)}")
        print(f"  Vector dimension: 768")
        print(f"  Metric: Cosine similarity\n")
        
        # Show stored vectors
        print(f"Stored Vector Embeddings:\n")
        for i, (vec_id, vec_data) in enumerate(list(vectors.items())[:5], 1):
            print(f"  {i}. ID: {vec_id[:30]}...")
            if isinstance(vec_data, dict) and 'embedding' in vec_data:
                emb = vec_data['embedding']
                print(f"     Embedding sample: [{emb[0]:.4f}, {emb[1]:.4f}, {emb[2]:.4f}, ...]")
            print(f"     Type: {type(vec_data)}")
        
        # Try semantic search
        print(f"\n\nSemantic Search Example:")
        print(f"Query: 'What products are available?'\n")
        
        # Get embedding for query
        query_embedding = await embedding_func("What products are available?")
        print(f"Query embedding generated: {len(query_embedding)} dimensions")
        print(f"Sample: [{query_embedding[0]:.4f}, {query_embedding[1]:.4f}, {query_embedding[2]:.4f}, ...]\n")
        
        print(f"✓ Vector DB ready for semantic similarity search")
        
    except Exception as e:
        print(f"Error: {e}")


def query_graph_db():
    """Query the Graph Database (Neo4j)"""
    print("\n" + "="*70)
    print("GRAPH DATABASE QUERIES (Neo4j)")
    print("="*70 + "\n")
    
    uri = os.environ.get('NEO4J_URI', 'neo4j://localhost:7687')
    user = os.environ.get('NEO4J_USERNAME', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD', 'password')
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Get statistics
            print(f"Neo4j Connection: ✓ Connected to {uri}\n")
            
            # Count nodes
            result = session.run("MATCH (n) RETURN COUNT(n) as count")
            record = result.single()
            node_count = record['count'] if record else 0
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN COUNT(r) as count")
            record = result.single()
            rel_count = record['count'] if record else 0
            
            print(f"Graph Statistics:")
            print(f"  Total nodes: {node_count}")
            print(f"  Total relationships: {rel_count}\n")
            
            # Query 1: Find all node labels
            print(f"Query 1: Find all node types")
            result = session.run("CALL db.labels() YIELD label RETURN label")
            labels = [record['label'] for record in result]
            if labels:
                print(f"  Node types: {', '.join(labels)}")
            else:
                print(f"  No custom node types (using default storage)")
            
            # Query 2: Sample nodes
            print(f"\nQuery 2: Sample nodes from database")
            result = session.run("MATCH (n) RETURN n LIMIT 5")
            records = list(result)
            print(f"  Found {len(records)} sample nodes:")
            for rec in records:
                node = rec['n']
                print(f"    - {dict(node)}")
            
            # Query 3: Relationship types
            print(f"\nQuery 3: Find relationship types")
            result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
            rel_types = [record['relationshipType'] for record in result]
            if rel_types:
                print(f"  Relationship types: {', '.join(rel_types)}")
            else:
                print(f"  No custom relationship types")
            
            # Query 4: Graph structure
            print(f"\nQuery 4: Graph structure sample")
            result = session.run("""
                MATCH (n)-[r]->(m) 
                RETURN type(r) as rel_type, COUNT(*) as count 
                LIMIT 5
            """)
            records = list(result)
            if records:
                print(f"  Relationship distribution:")
                for rec in records:
                    print(f"    - {rec['rel_type']}: {rec['count']} edges")
            else:
                print(f"  No relationships found")
            
            print(f"\n✓ Graph DB ready for relationship queries")
        
        driver.close()
        
    except Exception as e:
        print(f"Neo4j Error: {e}")
        print(f"Make sure Neo4j is running: docker compose ps")


async def hybrid_query_demo():
    """Demo a hybrid query using both DBs"""
    print("\n" + "="*70)
    print("HYBRID QUERY DEMO (Vector + Graph)")
    print("="*70 + "\n")
    
    print(f"Example hybrid workflow:\n")
    print(f"1. User asks: 'Show me electronics under $50'")
    print(f"   ├─ Graph DB: Match (p:Product) WHERE p.category='Electronics' AND p.price<50")
    print(f"   └─ Vector DB: Semantic search for 'affordable electronics'")
    print(f"\n2. Combine results from both sources")
    print(f"3. Return ranked hybrid results")
    print(f"\nYou can now:")
    print(f"  • Search by semantic meaning (Vector DB)")
    print(f"  • Search by exact relationships (Graph DB)")
    print(f"  • Combine both for powerful hybrid search")


async def main():
    print("\n" + "="*70)
    print("STORAGE LAYER DEMONSTRATION")
    print("Vector DB + Graph DB Query Examples")
    print("="*70)
    
    # Query vector DB
    await query_vector_db()
    
    # Query graph DB
    query_graph_db()
    
    # Show hybrid capability
    await hybrid_query_demo()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70 + "\n")
    print("1. Run queries on stored data:")
    print("   python storage_query.py")
    print("\n2. Direct Neo4j access:")
    print("   cypher-shell -u neo4j -p password")
    print("\n3. Hybrid queries in Python:")
    print("   from lightrag import LightRAG")
    print("   rag = LightRAG(working_dir='./rag_local')")
    print("   result = await rag.aquery('Your question here')")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
