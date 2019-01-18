#' Add Sequential ID Number To Data Frame Based On FastLink Matches
#'
#' @param df The data frame of interest
#' @param match_obj The fastLink list containing matching rows or a stacked data 
#'   frame of matches with the class "fmr_stack_fastLink_matches"
#'
#' @return
#' @export
#'
#' @examples
#' #> Not run
#' #> df_unique_combo_w_id <- fmr_add_unique_id(df_unique_combo, fastlink_out)
#' #> df_unique_combo_w_id
#' 
#' #> # A tibble: 7 x 10
#' #>      id incident nm_first nm_last sex   birth_mnth birth_year add_num add_street group                        
#' #>   <int>    <dbl> <chr>    <chr>   <chr>      <dbl>      <dbl>   <dbl> <chr>      <chr>                        
#' #> 1     2     1003 jane     smith   f              2       1937      14 elm        jane_smith_1937_2_14_elm     
#' #> 2     2     1005 jane     smith   f              3       1937      14 elm        jane_smith_1937_3_14_elm     
#' #> 3     3     1006 joy      smith   f              8       1941     101 main       joy_smith_1941_8_101_main    
#' #> 4     4     1008 amy      jones   f              1       1947    1405 texas      amy_jones_1947_1_1405_texas  
#' #> 5     1     1001 john     smith   m              9       1936     101 main       john_smith_1936_9_101_main   
#' #> 6     1     1004 jon      smith   m              9       1936     101 main       jon_smith_1936_9_101_main    
#' #> 7     1     1007 michael  smith   m              9       1936     101 main       michael_smith_1936_9_101_main
fmr_add_match_id <- function(df, match_obj) {
  
  # ===========================================================================
  # Create tibble of matching rows
  # ===========================================================================
  
  # Turn fastLink results into tibble of rows and their matches
  matches <- tibble::tibble(
    row = match_obj$matches$inds.b,
    matching_row = match_obj$matches$inds.a
  )
  
  # Nest all matches for each row
  matches <- matches %>% 
    dplyr::group_by(row) %>% 
    dplyr::mutate(matches = list(matching_row)) %>%
    dplyr::ungroup()
  
  # Reduce to unique sets of matching rows
  # i.e. 1,2,3 is the same as 3,2,1
  matches <- matches %>% 
    dplyr::mutate(matches = purrr::map_chr(
      matches,
      function(x) {
        x = sort(x) # 1,2,3 is the same as 3,2,1
        x = paste(x, collapse = ",") # Convert list to character string
        x
      })
    ) %>% 
    dplyr::select(matches) %>%
    distinct() # Reduce to 1 row per group of matches
  
  # Sequentially number each group of matches
  # This will become the unique id
  matches <- matches %>%
    dplyr::mutate(
      id = row_number(),
      row = purrr::map( # Turn back into list
        matches,
        ~ scan(text = ., what = 0L, sep = ",", quiet = TRUE)
      )
    ) 
  
  # Covert to data frame with the appropriate id number for each row in the 
  # original data set
  matches <- matches %>%
    tidyr::unnest() %>% 
    dplyr::select(id, row)
  
  # Join id number back to original data set
  out <- matches %>% 
    dplyr::right_join(
      df %>% 
        dplyr::mutate(row = dplyr::row_number()),
      by = "row"
    ) %>% 
    select(-row)
  
  # ===========================================================================
  # Return original data frame with unique id added
  # ===========================================================================
  out
}