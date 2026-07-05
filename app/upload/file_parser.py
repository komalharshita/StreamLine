import io
import logging

import pandas as pd
from fastapi import HTTPException, status

logger = logging.getLogger("app.upload.file_parser")


class FileParser:
    """Safe dataset parser using Pandas to check validity and extract structure metadata."""

    @staticmethod
    def parse_and_get_dimensions(file_bytes: bytes, extension: str) -> tuple[int, int]:
        """Parses raw bytes based on extension.

        Returns a tuple of (row_count, column_count).
        Raises HTTPException if parsing fails (indicating file corruption or invalid contents).
        """
        logger.info(f"Parsing uploaded file stream with format extension: {extension}")

        try:
            if extension == ".csv":
                # Attempt to parse as CSV
                # Use a small sample check first or load layout
                # To prevent excessive RAM blowups on 100MB files, we could parse in chunks or just inspect shape
                # Since we need row count, we read the full file, but let's catch memory/parsing errors
                try:
                    # UTF-8 default, fall back to latin-1 if decoding fails
                    df = pd.read_csv(io.BytesIO(file_bytes))
                except UnicodeDecodeError:
                    logger.debug(
                        "UTF-8 decoding failed, retrying with latin-1 encoding."
                    )
                    df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1")

            elif extension in {".xlsx", ".xls"}:
                # Attempt to parse all sheets in the Excel file
                xls_dict = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
                if not xls_dict:
                    raise ValueError("The uploaded Excel workbook contains no sheets.")

                if len(xls_dict) == 1:
                    df = list(xls_dict.values())[0]
                else:
                    logger.info(f"Multi-sheet Excel workbook identified: {list(xls_dict.keys())}")
                    dfs = []
                    for s_name, s_df in xls_dict.items():
                        if not s_df.empty:
                            s_df_copy = s_df.copy()
                            # Inject source sheet name to trace schema rows
                            s_df_copy["_sheet_name"] = str(s_name)
                            dfs.append(s_df_copy)
                    
                    if dfs:
                        df = pd.concat(dfs, ignore_index=True)
                    else:
                        df = list(xls_dict.values())[0]

            else:
                raise ValueError(f"Unsupported parser extension: {extension}")

            rows, cols = df.shape
            logger.info(f"Successfully parsed file: rows={rows}, columns={cols}")
            return int(rows), int(cols), df

        except Exception as e:
            logger.error(
                f"File parsing check failed (file might be corrupted): {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"File upload rejected: The uploaded file appears to be corrupted or invalid. "
                    f"Details: {str(e)}"
                ),
            )
