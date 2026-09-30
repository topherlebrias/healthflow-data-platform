from extract import main as extract_main
from validate import main as validate_main
from transform import main as transform_main
from logger import start_run, finish_run
from state_manager import update_watermark
from storage import upload_file
from load_warehouse import main as load_warehouse_main
from lock_manager import acquire_lock, release_lock


def main():

    if not acquire_lock():

        print()
        print("=" * 60)
        print("HEALTHFLOW DATA PIPELINE")
        print("=" * 60)
        print()
        print("PIPELINE ALREADY RUNNING")
        print(
            "Another pipeline execution is currently active."
        )
        print(
            "This run will stop to prevent "
            "overlapping executions."
        )
        print()
        print("=" * 60)

        return

    run_info = start_run()

    print("=" * 60)
    print("HEALTHFLOW DATA PIPELINE")
    print("=" * 60)

    try:

        # =================================================
        # STEP 1: EXTRACT
        # =================================================

        print()
        print("STEP 1: EXTRACT")
        print("-" * 60)

        (
            records_extracted,
            pending_watermarks,
            extracted_files,
        ) = extract_main()

        print()
        print("UPLOADING RAW FILES TO DATA LAKE")
        print("-" * 60)

        for file_path in extracted_files:
            upload_file(file_path)

        # =================================================
        # STEP 2: VALIDATE
        # =================================================

        print()
        print("STEP 2: VALIDATE")
        print("-" * 60)

        (
            records_valid,
            records_rejected,
            successful_tables,
            rejected_tables,
        ) = validate_main()

        # =================================================
        # STEP 3: TRANSFORM
        # =================================================

        print()
        print("STEP 3: TRANSFORM")
        print("-" * 60)

        records_transformed = transform_main()

        # =================================================
        # STEP 4: LOAD WAREHOUSE
        # =================================================

        print()
        print("STEP 4: LOAD WAREHOUSE")
        print("-" * 60)

        load_warehouse_main()

        # =================================================
        # STEP 5: UPDATE WATERMARKS
        # =================================================

        print()
        print("STEP 5: UPDATE WATERMARKS")
        print("-" * 60)

        for table_name, watermark in pending_watermarks.items():

            if table_name in rejected_tables:

                print(
                    f"Keeping watermark unchanged for "
                    f"{table_name} because validation "
                    f"rejected records."
                )

                continue

            update_watermark(
                table_name,
                watermark,
            )

            print(
                f"Watermark updated for "
                f"{table_name}: {watermark}"
            )

        # =================================================
        # FINISH SUCCESSFULLY
        # =================================================

        finish_run(
            run_info,
            status="SUCCESS",
            records_extracted=records_extracted,
            records_valid=records_valid,
            records_rejected=records_rejected,
            records_transformed=records_transformed,
        )

        print()
        print("=" * 60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as error:

        finish_run(
            run_info,
            status="FAILED",
            error_message=str(error),
        )

        print()
        print("=" * 60)
        print("PIPELINE FAILED")
        print("=" * 60)

        print(
            f"Error: {error}"
        )

        raise

    finally:

        release_lock()


if __name__ == "__main__":
    main()