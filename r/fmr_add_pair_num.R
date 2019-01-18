#' Add Pair Numbers To Rows Of Matched Records
#' 
#' @description This function is intended to be used with `dplyr::mutate` and 
#'   as part of the process of fuzzy matching records. It sequentially numbers 
#'   every two rows in a data frame.
#'
#' @param df A data frame
#'
#' @return A vector of sequential numbers
#' @export
#'
#' @examples
#' tibble(
#'   name = c("jon", "john", "mary", "marry"),
#'   age = c(67, 67, 82, 82)
#' ) %>% 
#'   mutate(pair = add_pair_num(.))
#'   
#' #> # A tibble: 4 x 3
#' #>   name    age  pair
#' #>   <chr> <dbl> <int>
#' #> 1 jon      67     1
#' #> 2 john     67     1
#' #> 3 mary     82     2
#' #> 4 marry    82     2
fmr_add_pair_num <- function(df) {
  out <- seq(1, nrow(df) / 2) %>% rep(each = 2)
  out
}