#set page(margin: 2.5cm)
#set text(font: "Liberation Sans", size: 12pt)

#let data = json(bytes(sys.inputs.data))
#let table_header = ("ID", "Name", "Date of Birth", "Mobile Number")

#table(
  columns: (1fr, 2fr, 2fr, 2fr),
  align: (left, left, left, left),
  stroke: 1pt + black,
  inset: 5pt,
  fill: (x, y) => if y == 0 { rgb("#eeeeee") },

  // Header row (repeats on each page)
  table.header(
    repeat: true,
    [*#table_header.at(0)*],
    [*#table_header.at(1)*],
    [*#table_header.at(2)*],
    [*#table_header.at(3)*],
  ),

  // Data rows
  ..data.map(item => (
    [#item.at("id")],
    [#item.at("name")],
    [#item.at("dob")],
    [#item.at("mobile_number")],
  )).flatten()
)

