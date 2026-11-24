# FinWise – Viva Questions and Answers

Likely questions for a project demonstration, with short answers. Formulas and worked examples are in the [README](../README.md#how-the-calculations-work).

**Q1. What is the purpose of this project?**
FinWise helps users plan loans and investments. It calculates the monthly EMI and total interest for a loan, and the estimated future value of a SIP, with charts, schedules and downloadable reports.

**Q2. Why did you choose Streamlit?**
Streamlit turns a Python script into a web app without HTML/JavaScript frameworks. It has ready-made widgets (sliders, number inputs, tabs, download buttons) and reruns the script whenever an input changes, which gives real-time results.

**Q3. How does real-time calculation work?**
Every widget change makes Streamlit rerun `app.py` from top to bottom with the new values. The calculation functions run again and the page redraws.

**Q4. What is session state and why is it used?**
`st.session_state` is a dictionary that keeps values between reruns. FinWise uses it to keep the number box and slider in sync, to remember inputs when you switch pages, and to restore defaults when you press Reset.

**Q5. Explain the EMI formula.**
EMI = P × r × (1+r)^n / ((1+r)^n − 1), where P is the principal, r the monthly rate and n the number of months. It gives the fixed payment that clears both principal and interest in exactly n months.

**Q6. Why do we divide the annual rate by 12 and by 100?**
EMIs are monthly, so the rate must be per month (÷12). The rate is entered as a percentage, so ÷100 turns it into a decimal (8.5% → 0.085).

**Q7. What happens if the interest rate is 0?**
The denominator (1+r)^n − 1 becomes 0, which would cause a division-by-zero error. The code checks for this and uses EMI = P / n.

**Q8. What is an amortization schedule?**
A month-by-month table of each EMI split into interest and principal, with the opening and closing balance. It shows how the loan reduces over time.

**Q9. Why is the interest part higher in the early months?**
Interest is charged on the outstanding balance. The balance is highest at the start, so interest is highest then. As the balance falls, interest falls and more of the EMI goes to principal.

**Q10. What is a SIP?**
A Systematic Investment Plan is a way to invest a fixed amount in a mutual fund at regular intervals, usually monthly.

**Q11. Explain the SIP formula.**
M = P × [((1+i)^n − 1)/i] × (1+i). The bracket is the future value of a series of equal monthly payments. The extra (1+i) is there because each payment is made at the start of the month and earns one more month of return.

**Q12. Are SIP returns guaranteed?**
No. The calculator assumes a constant return to give an estimate. Real mutual fund returns depend on the market and can be lower or even negative. The app shows this warning clearly.

**Q13. What is compounding?**
Earning returns on earlier returns, not just on the original amount. That's why the gap between the invested and value lines on the SIP chart widens over time.

**Q14. Where did you use NumPy?**
In `sip_yearly_growth`, `np.arange` creates all the year numbers and the SIP formula runs on the whole array at once (vectorisation), with no loop. NumPy also creates the tick positions for the chart axes.

**Q15. Why Plotly instead of Matplotlib?**
Plotly charts are interactive: they have hover tooltips and zoom, and they look modern in a web app. Matplotlib produces static images.

**Q16. How does Indian Rupee formatting work?**
The Indian system keeps the last three digits together and then groups by twos (12,34,567). `format_inr` splits the number into the last three digits and the rest, groups the rest in pairs, and adds the ₹ sign.

**Q17. How is the CSV report generated?**
`build_csv_report` uses Python's `csv` module and pandas `to_csv` to write a summary block and the full table into an in-memory buffer (`io.StringIO`). `st.download_button` then serves it, so no file is saved on the server.

**Q18. What validation have you done?**
The inputs have minimum and maximum limits, so negative or empty values can't be entered. The calculation functions also raise errors for invalid values, and the app shows warnings for unusual values like interest above 20% or returns above 15%.

**Q19. What is the difference between flat and reducing-balance interest?**
Flat interest is charged on the original principal for the whole tenure. Reducing-balance interest is charged only on the outstanding amount. FinWise uses reducing balance, which is how most bank loans in India work.

**Q20. How can this project be extended?**
Add a step-up SIP, lumpsum and SWP calculators, loan prepayment simulation, comparison of two loans, PDF reports, inflation-adjusted values, user login to save plans, or deployment on Streamlit Community Cloud.

**Q21. How does the one-click launcher work?**
`run.bat` (Windows) or `run.sh`/`run.command` (Linux/macOS) finds a suitable Python and runs `launcher.py`. The launcher uses only the standard library. It creates a private virtual environment (`.venv`), installs `requirements.txt` once (it stores a SHA-256 hash of that file so it can tell when it changes), finds a free port, starts Streamlit and opens the browser when the health check at `/_stcore/health` answers.

**Q22. Why use a virtual environment?**
It keeps FinWise's packages separate from the rest of the computer. Other projects' versions can't break it, and the project can't break them. Deleting `.venv` removes everything it installed.
