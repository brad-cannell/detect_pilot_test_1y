#' Block (Stratify) A Data Frame Into New Data Frames Prior To Fuzzy Matching
#'
#' @param df The data frame to subset into blocks.
#' @param x The variable that contains the values to subset on - must be a column in df.
#' @param verbose Optional feedback for the user. Default is TRUE.
#' @param NA_explicit Replace NA with "Missing". Default is TRUE. If FALSE, then a 
#'   a data frame for x will not be created where x is NA.
#'
#' @return Creates a new data frame in the global environment for each value of x.
#' @export
#'
#' @examples
#' \dontrun{fmr_block_data(df_unique_combo, sex)}
fmr_block_data <- function(df, x, verbose = TRUE, NA_explicit = TRUE) {
  
  # ===========================================================================
  # Process inputs
  # ===========================================================================
  x <- rlang::enquo(x)
  x_chr <- rlang::quo_name(x)
  df_name <- deparse(substitute(df))
  
  
  # ===========================================================================
  # Error checks
  # ===========================================================================
  if (!("data.frame" %in% class(df))) {
    stop("df must be of class data.frame")
  }
  
  if (!(x_chr %in% names(df))) {
    stop(x, " is not a column in df")
  }
  
  
  # ===========================================================================
  # Create list of data frames stratified by values of x
  # ===========================================================================
  
  # Optionally make missing an explicit category 
  if (NA_explicit) {
    df[is.na(df[x_chr]), x_chr] <- "Missing"
  }
  
  # Create the list
  df_list <- split(df, df[x_chr])
  
  
  # ===========================================================================
  # Add blocked data frames to environment
  # ===========================================================================
  
  # Create empty vector to hold new data frame names
  new_df_list <- ""
  
  for (i in seq_along(df_list)) {
    
    # Add category level to data frame name
    new_df_i <- paste(df_name, names(df_list)[i], sep = "_")
    
    # Assign values to the new data frame name
    assign(new_df_i, df_list[[i]], envir = .GlobalEnv)
    
    # Save varnames as character string for verbose
    new_df_list <- c(new_df_list, paste("\n", new_df_i))
  }
  
  if (verbose) {
    cat(
      "The following data frames were created and added to the global",
      "environment by subsetting", df_name,
      "on the variable", x_chr, ":",
      new_df_list
    )
  }
}