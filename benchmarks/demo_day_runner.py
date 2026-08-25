import time
from axiom.services.model_gateway.client import ModelClient
from axiom.core.verification.smt_gateway import SmtGateway
from axiom.research.vector_store import VectorStore
from axiom.core.knowledge_graph.db import EpistemicStore
from axiom.core.knowledge_graph.schema import MathematicalClaimNode

def run_demo_iteration(iteration: int):
    start_time = time.time()
    try:
        # 1. Retrieval
        vs = VectorStore()
        # 2. Epistemic Node
        kg = EpistemicStore(":memory:")
        node = MathematicalClaimNode(
            id=f"claim_{iteration}",
            name="Quadratic Residue Conjecture",
            statement="x^2 = 3 mod 4 has no solutions"
        )
        kg.add_node(node)
        # 3. LLM Generation
        model = ModelClient()
        response = model.generate(
            prompt="Generate a mathematical hypothesis about quadratic residues modulo 4.",
            model="mock-model",
            temperature=0.0
        )
        # 4. SMT Verification
        gw = SmtGateway()
        is_valid, counterexample = gw.verify_modular_conjecture(
            equation="x * x == 3", 
            modulus=4, 
            variables=["x"]
        )
        duration = time.time() - start_time
        return True, duration, response, is_valid
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e), None

def main():
    successes = 0
    total_duration = 0.0
    print("Running Demo Day 10x Reliability Test...")
    for i in range(10):
        success, duration, msg, is_valid = run_demo_iteration(i)
        if success:
            successes += 1
            print(f"Run {i+1}/10: SUCCESS in {duration:.2f}s | Valid={is_valid}")
        else:
            print(f"Run {i+1}/10: FAILED in {duration:.2f}s | Error: {msg}")
        total_duration += duration
    
    sr = (successes / 10.0) * 100
    avg_dur = total_duration / 10.0
    print(f"\nDemo Success Rate: {sr}%")
    print(f"Average Duration: {avg_dur:.2f}s")
    
    with open("docs/DEMO_METRICS.md", "w") as f:
        f.write(f"# Demo Day Metrics\n")
        f.write(f"- **Demo Success Rate**: {sr}%\n")
        f.write(f"- **Average Duration**: {avg_dur:.2f}s\n")
        f.write(f"- **Runs**: 10\n")
        
if __name__ == "__main__":
    main()
