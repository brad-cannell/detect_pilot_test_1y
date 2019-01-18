#' Stack FastLink Matches For Easy Inspection
#' 
#' @description This function is intended to be used as part of the process of 
#'   fuzzy matching records. Specifically, when using the `fastLink` package, 
#'   I was unable to find a built-in function that made it easy to compare 
#'   rows that were returned as matches. 
#'   
#'   This function takes the list output from `fastLink::fastLink()` and the 
#'   data frame of interest (i.e., the data frame that contains the records 
#'   the users search for fuzzy matches).
#'   
#'   It then returns all pairs of rows from df that were found to be possible 
#'   matches – along with the other variables from df. Each pair of possibly 
#'   matching rows are stacked vertically for easy manual inspection.
#'
#' @param fastLink_obj a list of class 'fastLink' 
#' @param df data frame of interest (i.e., the data frame that contains the 
#'   records the users search for fuzzy matches)
#'
#' @return a tibble
#' @export
#'
#' @examples
#' #> Not run:
#' #> matches <- fmr_stack_fastLink_matches(fastlink_out, df_unique_combo)
#' #> head(matches) %>% select(1:8)
#' 
#' #> # A tibble: 6 x 8
#' #>     row  pair posterior_probability incident nm_first nm_last sex   birth_mnth
#' #>   <dbl> <int>                 <dbl>    <dbl> <chr>    <chr>   <chr>      <dbl>
#' #> 1     1     1                 1.000     1001 john     smith   m              9
#' #> 2     3     1                 1.000     1004 jon      smith   m              9
#' #> 3     1     2                 1.000     1001 john     smith   m              9
#' #> 4     5     2                 1.000     1006 joy      smith   f              8
#' #> 5     1     3                 1.000     1001 john     smith   m              9
#' #> 6     6     3                 1.000     1007 michael  smith   m              9
fmr_stack_fastLink_matches <- function(fastLink_obj, df) {
  
  # ===========================================================================
  # Error checks
  # ===========================================================================
  if (!("fastLink" %in% class(fastLink_obj))) {
    stop('fastLink_obj must be of class "fastLink"')
  }
  
  
  # ===========================================================================
  # Create data frame of potential matches to compare
  # ===========================================================================
  potential_matches <- tibble::tibble(
    row = fastLink_obj$matches$inds.b,
    matching_row = fastLink_obj$matches$inds.a,
    posterior_probability = fastLink_obj$posterior
  )
  
  # Keep only unique combinations of rows (e.g., not 1-3 and 3-1)
  potential_matches <- potential_matches %>%
    dplyr::mutate(
      combo = purrr::map2_chr(
        .x = row,
        .y = matching_row,
        .f = function(x, y) {
          min <- min(x, y)
          max <- max(x, y)
          out <- paste(min, max, sep = "_")
          out
        }
      ),
      dup = duplicated(combo)
    ) %>%
    dplyr::filter(!dup) %>%
    dplyr::select(-combo, -dup)
  
  
  # ===========================================================================
  # Manipulate the potential matches data frame
  # Stack row and matching row on top of each other
  # Add a pair number to each row and matching row
  # ===========================================================================
  stacked_potential_matches <- tibble::tibble(
    row = c(rbind(potential_matches[["row"]], potential_matches[["matching_row"]])),
    pair = rep(seq(1, length(row) / 2), each = 2),
    posterior_probability = rep(potential_matches[["posterior_probability"]], each = 2)
  )
  
  
  # ===========================================================================
  # Add substantive variables of interest to matched pairs for review
  # ===========================================================================
  out <- stacked_potential_matches %>% 
    dplyr::left_join(
      df %>% 
        dplyr::mutate(row = dplyr::row_number()),
      by = "row"
    )
  
  
  # ===========================================================================
  # Add a class identifier that can be used to change the behavior of 
  # downstream functions
  # ===========================================================================
  class(out) <- c(class(out), "fmr_stack_fastLink_matches")
  
  
  # ===========================================================================
  # Return data frame of potential matches to compare
  # ===========================================================================
  out
}