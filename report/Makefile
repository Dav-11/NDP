default: report.pdf

report.pdf: nc_lab_report.md
	pandoc $< -F mermaid-filter --pdf-engine=typst -o $@
