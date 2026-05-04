import time
import os
import pandas as pd

from src.models import Location
from src.pipeline import evaluate_location

def run_batch(
    manifest_path: str,
    set_name: str = "main",
    sleep_time: float = 2.0,
    retry_sleep: float = 10.0,
    retry_extra: float = 3.0,
    output_dir: str = "../data/results",
) -> pd.DataFrame:
    """
    Run the full evaluation pipeline over every row in a manifest CSV.
    Expects columns: id, snapped_lat, snapped_lng, city, state, environment.
    Images must already be fetched — this only runs evaluation.

    Retries any errored rows once after the full pass.
    Saves per-criterion rows to ../data/results/batch_{set_name}.csv.
    """
    df = pd.read_csv(manifest_path)
    total = len(df)
    all_rows = []
    errors = []

    def run_single(row) -> list[dict]:
        loc = Location(lat=row["snapped_lat"], lng=row["snapped_lng"])
        evaluation = evaluate_location(loc, int(row["id"]), set_name)
        rows = []
        for result in evaluation["results"]:
            rows.append({
                "id":          row["id"],
                "city":        row["city"],
                "state":       row["state"],
                "environment": row["environment"],
                "criterion":   result.criterion,
                "passed":      result.passed,
                "importance":  result.importance.value if result.importance else None,
                "notes":       result.notes,
            })
        return rows

    for _, row in df.iterrows():
        print(f"\n[{int(row['id'])}/{total}] {row['city']}, {row['state']}")
        try:
            rows = run_single(row)
            all_rows.extend(rows)
        except Exception as e:
            print(f"  ERROR: {e}")
            errors.append(row)
        time.sleep(sleep_time)

    if errors:
        print(f"\n── Retrying {len(errors)} failed stops ──")
        time.sleep(retry_sleep)
        for row in errors:
            print(f"  retrying ID {int(row['id'])}...")
            try:
                rows = run_single(row)
                all_rows.extend(rows)
            except Exception as e:
                print(f"  ERROR again: {e}")
                all_rows.append({
                    "id": row["id"], "city": row["city"], "state": row["state"],
                    "environment": row["environment"],
                    "criterion": "BATCH_ERROR", "passed": None,
                    "importance": None, "notes": str(e),
                })
            time.sleep(retry_extra)

    results_df = pd.DataFrame(all_rows)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"batch_{set_name}.csv")
    results_df.to_csv(out_path, index=False)

    print(f"\n═══ Batch complete: {set_name} ═══")
    print(f"Stops evaluated : {total}")
    by_criterion = results_df[results_df["criterion"] != "BATCH_ERROR"].groupby("criterion")
    for criterion, group in by_criterion:
        passed  = (group["passed"] == True).sum()
        failed  = (group["passed"] == False).sum()
        none    = group["passed"].isna().sum()
        print(f"  {criterion:<20} ✅ {passed}  ❌ {failed}  ⚠️  {none}")

    return results_df