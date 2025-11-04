"""Test script to verify the plot endpoint fix."""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.wolfram.language_eval_client import WolframLanguageEvalClient


async def test_plot_fix():
    """Test the plot functionality with the fix."""
    print("Testing plot functionality...")

    try:
        async with WolframLanguageEvalClient() as client:
            result = await client.plot(
                expression="sin(x)",
                variable="x",
                range_min=-10,
                range_max=10,
                plot_type="Plot"
            )

            print(f"Success: {result.get('success')}")
            print(f"Output: {result.get('output')}")
            print(f"Error: {result.get('error')}")
            print(f"Output type: {result.get('output_type')}")

            # Check if we got a successful response
            if result.get('success'):
                print("✅ Plot generation successful!")
                if "plot" in result.get('output', '').lower():
                    print("✅ Output appears to be a plot URL")
                else:
                    print("⚠️ Output doesn't look like a plot URL")
            else:
                print("❌ Plot generation failed")
                if result.get('error'):
                    print(f"Error details: {result['error']}")

    except Exception as e:
        print(f"❌ Exception during test: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_plot_fix())
