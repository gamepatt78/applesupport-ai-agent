# AppleSupport Customer Question Bank

Use these questions in the app at `http://127.0.0.1:5000/`.

## Account Access

1. My Apple ID is locked. How can I log in?
2. I forgot my Apple ID password. What should I do?
3. I cannot sign in to iCloud.
4. How do I recover my Apple account?
5. My verification code is not working.
6. I cannot access my Apple ID after changing my phone number.
7. Why has my account been disabled?
8. How can I reset my iCloud password?
9. I am locked out of my account.
10. I cannot remember my Apple ID email address.

Expected intent: `account_access`
Expected action: Auto-handle unless there is suspicious activity.

## Billing and Refunds

11. I was charged twice for my iCloud subscription.
12. How can I request a refund?
13. I do not recognize this Apple charge.
14. Why was my card charged for an app?
15. How can I cancel my subscription?
16. My payment was declined.
17. I was charged after cancelling my subscription.
18. Where can I see my purchase history?
19. I need a refund for an accidental purchase.
20. Why did my subscription renew automatically?

Expected intent: `billing_refund`
Expected action: Auto-handle routine billing questions; escalate fraud or chargeback concerns.

## Device Setup

21. How do I set up my new iPhone?
22. How do I transfer data from my old iPhone?
23. My iPhone will not activate.
24. How do I restore my iPhone from a backup?
25. How do I set up iCloud on my new device?
26. What should I do before transferring to a new iPhone?
27. My activation is stuck.
28. How do I move my photos to my new iPhone?
29. How can I restore my device?
30. My new iPhone cannot complete setup.

Expected intent: `device_setup`
Expected action: Auto-handle.

## Software Troubleshooting

31. My iPhone battery is draining quickly after the latest iOS update.
32. An app keeps crashing on my iPhone.
33. My iPhone is not working after the update.
34. How do I update iOS?
35. My phone keeps showing an error message.
36. Why is my iPhone running slowly?
37. The latest software update failed.
38. My Apple app will not open.
39. My iPhone freezes when I use certain apps.
40. How do I fix an iOS software problem?

Expected intent: `software_troubleshooting`
Expected action: Auto-handle routine troubleshooting.

## Repair and Warranty

41. My iPhone screen is broken. Can I get it repaired?
42. How much does a battery replacement cost?
43. Is my iPhone covered by warranty?
44. My device stopped working. What are my repair options?
45. How do I find an Apple Authorized Service Provider?
46. Can I replace my damaged iPhone?
47. How do I check my AppleCare coverage?
48. My iPhone has water damage.
49. My battery is swollen. What should I do?
50. Can I get a repair appointment?

Expected intent: `repair_warranty`
Expected action: Auto-handle basic coverage information; escalate safety issues such as swollen batteries.

## Order and Delivery

51. Where is my iPhone order?
52. How can I track my Apple order?
53. My order has not arrived yet.
54. When will my order be delivered?
55. My tracking information has not updated.
56. Can I change my delivery address?
57. My Apple order was cancelled.
58. The package says delivered but I cannot find it.
59. How do I return an Apple product?
60. Can I change the delivery date?

Expected intent: `order_delivery`
Expected action: Auto-handle routine tracking; escalate missing or disputed deliveries.

## Store Support

61. Where is the nearest Apple Store?
62. How do I book a Genius Bar appointment?
63. Can I visit an Apple Store without an appointment?
64. What are the Apple Store opening hours?
65. How do I schedule a repair at the Apple Store?
66. Does the Apple Store near me have this product?
67. How can I contact an Apple Store?
68. Can I pick up my order at an Apple Store?
69. Where can I get technical help in a store?
70. How do I change my Genius Bar appointment?

Expected intent: `store_support`
Expected action: Auto-handle.

## General Questions

71. What products does Apple sell?
72. How do I contact Apple Support?
73. Where can I find Apple support documentation?
74. What is AppleCare?
75. How can I learn more about iCloud?
76. What are the latest iPhone features?
77. How do I contact Apple by phone?
78. Where can I find Apple user guides?
79. Does Apple offer student discounts?
80. How do I give feedback to Apple?

Expected intent: `general_inquiry`
Expected action: Auto-handle when the question is informational.

## Escalation and Human Review

81. Someone hacked my Apple account.
82. I think someone stole my iPhone.
83. This is fraud and I want to dispute the charge.
84. My account has suspicious activity.
85. I am contacting my lawyer about this issue.
86. I will file a lawsuit if this is not resolved.
87. Someone is using my payment card through Apple.
88. My stolen phone contains sensitive information.
89. I need to report an Apple security incident.
90. This issue involves a legal complaint.

Expected action: Escalate to a human.
Expected reason: Security, fraud, legal, stolen device, or chargeback risk.

## How to Test

1. Start the app with `python app.py`.
2. Open `http://127.0.0.1:5000/`.
3. Copy one question into the message box.
4. Click **Analyze message**.
5. Compare the detected intent and action with the expected result above.
6. Record incorrect results for the failure-analysis section of the assignment.
