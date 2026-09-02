# Connect PhysiCode Finance to Google Sheets and Drive

The connector automatically creates a `PhysiCode Finance Tracker` spreadsheet and a `PhysiCode Invoices & Receipts` Drive folder in your Google account.

1. Open [Google Apps Script](https://script.google.com) and choose **New project**.
2. Replace `Code.gs` with the contents of [`google-apps-script/Code.gs`](google-apps-script/Code.gs).
3. Choose **Deploy → New deployment → Web app**.
4. Set **Execute as** to **Me**. Choose the access level appropriate for your team. For this local prototype, **Anyone** is simplest; keep the generated URL private.
5. Authorize Sheets and Drive access, then copy the Web App URL ending in `/exec`.
6. In PhysiCode Finance, open **Integrations**, paste the URL and save.

Opening the URL directly confirms the connector is running and creates the spreadsheet and folder. New grants, earnings and expenses append to their own tabs, while invoices are uploaded to Drive and linked in the expense sheet.

For a public multi-user deployment, add proper authentication and keep the connector URL server-side.
