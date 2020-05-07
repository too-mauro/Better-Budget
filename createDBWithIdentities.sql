USE [master]
GO
/****** Object:  Table [dbo].[ACCOUNTS]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ACCOUNTS](
	[ACCOUNT_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[USER_KEY] [bigint] NOT NULL,
	[ACCT_NAME] [varchar](1024) NOT NULL,
	[BALANCE] [decimal](18, 2) NOT NULL,
	[BANK_NAME] [varchar](1024) NOT NULL,
	[TYPE] [varchar](1024) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[ACCOUNT_ID] ASC,
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[BBUDG_USERS]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BBUDG_USERS](
	[USER_KEY] [bigint] IDENTITY(1,1) NOT NULL,
	[USER_NAME] [varchar](900) NOT NULL,
	[USER_EMAIL] [varchar](900) NOT NULL,
	[USER_HASHEDPASS] [varchar](1024) NOT NULL,
	[USER_REGISTERED_FROM_IP] [varchar](30) NOT NULL,
	[USER_REGISTERED_DTTM] [datetime] NOT NULL,
	[USER_AUTH_TOKEN] [uniqueidentifier] NOT NULL,
	[USER_AUTH_TOKEN_EXP_DTTM] [datetime] NOT NULL,
	[USER_DEACTIVATED_INDICATOR] [varchar](1) NOT NULL,
 CONSTRAINT [PK_USERKEY] PRIMARY KEY NONCLUSTERED 
(
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[BUDGET_POOL]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BUDGET_POOL](
	[BUDGET_PL_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[USER_KEY] [bigint] NOT NULL,
	[BUDGET_ID] [bigint] NOT NULL,
	[ITEM_NAME] [varchar](1024) NOT NULL,
	[AMOUNT_BUDGETED] [decimal](18, 2) NULL,
	[AMOUNT_SPENT] [decimal](18, 2) NULL,
	[TYPE] [varchar](1024) NULL,
PRIMARY KEY CLUSTERED 
(
	[BUDGET_PL_ID] ASC,
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[BUDGET_TRANSACTION]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BUDGET_TRANSACTION](
	[BUDGET_TRANS_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[USER_KEY] [bigint] NOT NULL,
	[BUDGET_PL_ID] [bigint] NOT NULL,
	[BUDGET_ID] [bigint] NOT NULL,
	[AMOUNT_SPENT] [decimal](18, 2) NOT NULL,
	[ACCOUNT_ID] [bigint] NOT NULL,
	[TRANSACTION_DATE] [datetime] NOT NULL,
	[VENDOR_DESC] [varchar](1024) NOT NULL,
	[LOCATION_DESC] [varchar](1024) NOT NULL,
	[ITEM_DESC] [varchar](1024) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[BUDGET_TRANS_ID] ASC,
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[BUDGETS]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[BUDGETS](
	[BUDGET_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[USER_KEY] [bigint] NOT NULL,
	[BUDGET_MONTH_NUM] [int] NOT NULL,
	[BUDGET_YEAR_NUM] [int] NOT NULL,
	[BUDGET_MONTH_YEAR] [varchar](15) NOT NULL,
	[BUDGET_TYPE] [varchar](1024) NOT NULL,
	[EXPECTED_INCOME] [decimal](18, 2) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[BUDGET_ID] ASC,
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[EVENT_LOGS]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EVENT_LOGS](
	[EVENT_KEY] [bigint] IDENTITY(1,1) NOT NULL,
	[EVENT_TYPE] [varchar](30) NOT NULL,
	[EVENT_TEXT] [varchar](4000) NOT NULL,
	[EVENT_DTTM] [datetime] NOT NULL,
	[EVENT_IP_ADDR] [varchar](30) NULL,
PRIMARY KEY CLUSTERED 
(
	[EVENT_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[INCOME]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[INCOME](
	[INCOME_ID] [bigint] NOT NULL,
	[USER_KEY] [bigint] NOT NULL,
	[INCOME_SOURCE] [varchar](1024) NOT NULL,
	[INCOME_DATE] [datetime] NOT NULL,
	[INCOME_AMT] [decimal](18, 2) NOT NULL,
	[BUDGET_ID] [bigint] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[INCOME_ID] ASC,
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[SAVINGS_CATEGORIES]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SAVINGS_CATEGORIES](
	[SAVINGS_CATEGORIES_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[USER_KEY] [bigint] NOT NULL,
	[CATEGORY_NAME] [varchar](1024) NOT NULL,
	[ACCT_NAME] [varchar](1024) NOT NULL,
	[BALANCE] [decimal](18, 2) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[SAVINGS_CATEGORIES_ID] ASC,
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[SAVINGS_TRANSFERS]    Script Date: 3/26/2020 1:40:30 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SAVINGS_TRANSFERS](
	[SAVING_TRANSFER_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[USER_KEY] [bigint] NOT NULL,
	[SAVINGS_CATEGORY] [varchar](1024) NOT NULL,
	[TARGET_ACCT] [varchar](1024) NOT NULL,
	[SOURCE_ACCT] [varchar](1024) NOT NULL,
	[TRANSFER_AMOUNT] [decimal](18, 2) NOT NULL,
	[NOTE] [varchar](1024) NULL,
PRIMARY KEY CLUSTERED 
(
	[SAVING_TRANSFER_ID] ASC,
	[USER_KEY] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
ALTER TABLE [dbo].[BBUDG_USERS] ADD  DEFAULT ('N') FOR [USER_DEACTIVATED_INDICATOR]
GO
ALTER TABLE [dbo].[EVENT_LOGS] ADD  DEFAULT (getdate()) FOR [EVENT_DTTM]
GO
ALTER TABLE [dbo].[ACCOUNTS]  WITH CHECK ADD FOREIGN KEY([USER_KEY])
REFERENCES [dbo].[BBUDG_USERS] ([USER_KEY])
GO
ALTER TABLE [dbo].[BUDGET_POOL]  WITH CHECK ADD FOREIGN KEY([BUDGET_ID], [USER_KEY])
REFERENCES [dbo].[BUDGETS] ([BUDGET_ID], [USER_KEY])
GO
ALTER TABLE [dbo].[BUDGET_TRANSACTION]  WITH CHECK ADD FOREIGN KEY([BUDGET_PL_ID], [USER_KEY])
REFERENCES [dbo].[BUDGET_POOL] ([BUDGET_PL_ID], [USER_KEY])
GO
ALTER TABLE [dbo].[BUDGETS]  WITH CHECK ADD FOREIGN KEY([USER_KEY])
REFERENCES [dbo].[BBUDG_USERS] ([USER_KEY])
GO
ALTER TABLE [dbo].[INCOME]  WITH CHECK ADD FOREIGN KEY([BUDGET_ID], [USER_KEY])
REFERENCES [dbo].[BUDGETS] ([BUDGET_ID], [USER_KEY])
GO
ALTER TABLE [dbo].[INCOME]  WITH CHECK ADD FOREIGN KEY([USER_KEY])
REFERENCES [dbo].[BBUDG_USERS] ([USER_KEY])
GO
ALTER TABLE [dbo].[SAVINGS_CATEGORIES]  WITH CHECK ADD FOREIGN KEY([USER_KEY])
REFERENCES [dbo].[BBUDG_USERS] ([USER_KEY])
GO
ALTER TABLE [dbo].[SAVINGS_TRANSFERS]  WITH CHECK ADD FOREIGN KEY([USER_KEY])
REFERENCES [dbo].[BBUDG_USERS] ([USER_KEY])
GO
