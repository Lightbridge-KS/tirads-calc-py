
#' New "TIRADS_report" class
#'
#' @param x A list
#'
#' @return `TIRADS_report` class appended
#' @noRd
new_TIRADS_report <- function(x = list()) {

  stopifnot(inherits(x, "list"))
  class(x) <- c("TIRADS_report", class(x))
  x

}

# TIRADS Calculator -------------------------------------------------------


#' ACR TIRADS Calculator
#'
#' Calculate [ACR TIRADS](https://www.acr.org/Clinical-Resources/Reporting-and-Data-Systems/TI-RADS) score, category level, and whether follow up or FNA should be done.
#'
#' @param composition (character) Internal components of a nodule,
#' must be one of "cystic", "spongiform","mixed", or "solid".
#' @param echogenicity (character) Level of echogenicity of the solid part,
#' relative to surrounding thyroid tissue. One of: "an" (anechoic), "hyper" (hyperechoic),
#' "iso" (isoechoic), "hypo" (hypoechoic), or "very-hypo" (very hypoechoic).
#' @param shape (character) Shape of the nodule, one of: "wider" (wider-than-tall) or "taller" (taller-than-wide).
#' @param margin (character) Margin of the nodule, one of: "smooth", "ill-defined", "lobulated", "irregular",
#' or "extra" (extrathyroidal extension)
#' @param echogenic_foci (character) Can choose > 1: "none-comet" (none or large comet-tail artifacts), "macro-calc" (macrocalcification),
#' "rim-calc" (rim calcification), or "punctate" (punctate echogenic foci).
#' @param size_cm (Numeric) Size of the nodule in cm.
#'
#' @return A list with "TIRADS_report" class containing:
#' * \strong{level}: (Character) A TIRADS category level.
#' * \strong{tot_points}: (Numeric) A total TIRADS score.
#' * \strong{points}: (Numeric) TIRADS scores for each categories.
#' * \strong{should_FNA}: (Logical) `TRUE` if FNA is suggested.
#' * \strong{should_follow}: (Logical) `TRUE` if follow-up is suggested.
#'
#' @seealso
#' * [ACR TIRADS (Thyroid Imaging Reporting & Data System)](https://www.acr.org/Clinical-Resources/Reporting-and-Data-Systems/TI-RADS)
#'
#' @export
#'
#' @examples
TIRADS_calc <- function(
    composition,
    echogenicity,
    shape,
    margin,
    echogenic_foci,
    size_cm = NA
) {

  pt_ls <- get_tirads_points(
    composition, echogenicity,
    shape, margin, echogenic_foci
  )

  tot_points <- sum(pt_ls[["points"]])

  tirads_lvs <- c("TR1" = "Benign",
                  "TR2" = "Not Suspicious",
                  "TR3" = "Mildly Suspicious",
                  "TR4" = "Moderately Suspicious",
                  "TR5" = "Highly Suspicious")

  lv <- if (tot_points >= 7L) {
    tirads_lvs[5]
  } else if(tot_points >= 4L) {
    tirads_lvs[4]
  } else if(tot_points == 0L){
    tirads_lvs[1]
  } else {
    tirads_lvs[tot_points]
  }
  ## FNA ?
  should_FNA <- any(
    c(tot_points == 3L & size_cm >= 2.5),
    c(tot_points >= 4L & tot_points <= 6L & size_cm >= 1.5),
    c(tot_points >= 7L & size_cm >= 1L)
  )

  ## Follow-up ?
  should_follow <- any(
    c(tot_points == 3L & size_cm >= 1.5),
    c(tot_points >= 4L & tot_points <= 6L & size_cm >= 1L),
    c(tot_points >= 7L & size_cm >= 0.5)
  )

  out <- list(
    level = lv,
    tot_points = tot_points,
    points = pt_ls[["points"]],
    should_FNA = should_FNA,
    should_follow = should_follow
  )

  # Add "TIRADS_report" class
  new_TIRADS_report(out)

}

# TIRADS Points -----------------------------------------------------------


#' Get ACR TIRADS score
#'
#' Calculate ACR TIRADS score from each 5 categories.
#'
#' @param composition (character) Internal components of a nodule,
#' must be one of "cystic", "spongiform","mixed", or "solid".
#' @param echogenicity (character) Level of echogenicity of the solid part,
#' relative to surrounding thyroid tissue. One of: "an" (anechoic), "hyper" (hyperechoic),
#' "iso" (isoechoic), "hypo" (hypoechoic), or "very-hypo" (very hypoechoic).
#' @param shape (character) Shape of the nodule, one of: "wider" (wider-than-tall) or "taller" (taller-than-wide).
#' @param margin (character) Margin of the nodule, one of: "smooth", "ill-defined", "lobulated", "irregular",
#' or "extra" (extrathyroidal extension)
#' @param echogenic_foci (character) Can choose > 1: "none", "comet" (large comet-tail artifacts), "macro-calc" (macrocalcification),
#' "rim-calc" (rim calcification), or "punctate" (punctate echogenic foci).
#'
#' @return A list with 2 elements:
#' * \strong{`points`}: for score from each 5 categories.
#' * \strong{`categories`}: values from each selected categories.
#'
#' @noRd
get_tirads_points <- function(
    composition,
    echogenicity,
    shape,
    margin,
    echogenic_foci
) {

  ## Match Args

  composition <- rlang::arg_match(
    composition, c("cystic", "spongiform","mixed", "solid")
  )
  echogenicity <- rlang::arg_match(
    echogenicity, c("an", "hyper", "iso", "hypo", "very-hypo")
  )
  shape <- rlang::arg_match(shape, c("wider", "taller"))
  margin <- rlang::arg_match(
    margin, c("smooth", "ill-defined", "lobulated", "irregular", "extra")
  )
  echogenic_foci <- rlang::arg_match(
    echogenic_foci, values = c("none", "comet", "macro-calc",
                               "rim-calc", "punctate"),
    multiple = TRUE # Can ≥ 1
  )

  if(any(duplicated(echogenic_foci))) cli::cli_abort("Value of {.code echogenic_foci} can not be duplicated.")


  pt <- vector("integer") # Init Empty Vector to Store

  pt["composition"] <-
    switch (composition,
            "cystic" = 0L,
            "spongiform" = 0L,
            "mixed" = 1L,
            "solid" = 2L
    )

  pt["echogenicity"] <-
    switch (echogenicity,
            "an" = 0L,
            "hyper" = 1L,
            "iso" = 1L,
            "hypo" = 2L,
            "very-hypo" = 3L
    )

  pt["shape"] <-
    switch (shape,
            "wider" = 0L,
            "taller" = 3L
    )

  pt["margin"] <-
    switch (margin,
            "smooth" = 0L,
            "ill-defined" = 0L,
            "lobulated" = 2L,
            "irregular" = 2L,
            "extra" = 3L
    )

  ## Echogenic Foci (Multi-select)
  foci <- c("none" = 0L, "comet" = 0L, "macro-calc" = 1L,
            "rim-calc" = 2L, "punctate" = 3L)

  pt["echogenic_foci"] <- sum(foci[echogenic_foci])

  ## Combine Output
  list(
    points = pt,
    categories = list(
      composition = composition,
      echogenicity = echogenicity,
      shape = shape,
      margin = margin,
      echogenic_foci = echogenic_foci
    )
  )
}
