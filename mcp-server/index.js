const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const {
  ListResourcesRequest,
  ReadResourceRequest,
  ListResourceTemplatesRequest,
} = require("@modelcontextprotocol/sdk/types.js");

// AWS SDK clients
const {
  EC2Client,
  DescribeVpcsCommand,
  DescribeSubnetsCommand,
  DescribeRouteTablesCommand,
  DescribeInternetGatewaysCommand,
  DescribeNatGatewaysCommand,
  DescribeSecurityGroupsCommand,
} = require("@aws-sdk/client-ec2");
const {
  CloudFrontClient,
  ListDistributionsCommand,
} = require("@aws-sdk/client-cloudfront");
const {
  ELBv2Client,
  DescribeLoadBalancersCommand,
  DescribeTargetGroupsCommand,
  DescribeListenersCommand,
  DescribeRulesCommand,
} = require("@aws-sdk/client-elastic-load-balancing-v2");
const {
  Route53ResolverClient,
  ListResolverEndpointsCommand,
  ListResolverRulesCommand,
} = require("@aws-sdk/client-route53resolver");
const {
  CloudWatchClient,
  ListMetricsCommand,
  GetMetricDataCommand,
} = require("@aws-sdk/client-cloudwatch");
const {
  CloudWatchLogsClient,
  DescribeLogGroupsCommand,
  FilterLogEventsCommand,
} = require("@aws-sdk/client-cloudwatch-logs");
const {
  S3Client,
  ListBucketsCommand,
  ListObjectsV2Command,
} = require("@aws-sdk/client-s3");
const {
  IAMClient,
  ListUsersCommand,
  ListRolesCommand,
  ListPoliciesCommand,
} = require("@aws-sdk/client-iam");
const {
  OrganizationsClient,
  ListAccountsCommand,
  ListOrganizationalUnitsForParentCommand,
} = require("@aws-sdk/client-organizations");
const {
  STSClient,
  GetCallerIdentityCommand,
} = require("@aws-sdk/client-sts");
const {
  KMSClient,
  ListKeysCommand,
} = require("@aws-sdk/client-kms");
const {
  SecretsManagerClient,
  ListSecretsCommand,
} = require("@aws-sdk/client-secrets-manager");
const {
  SSMClient,
  DescribeParametersCommand,
} = require("@aws-sdk/client-ssm");
const {
  SQSClient,
  ListQueuesCommand,
} = require("@aws-sdk/client-sqs");
const {
  SNSClient,
  ListTopicsCommand,
} = require("@aws-sdk/client-sns");
const {
  LambdaClient,
  ListFunctionsCommand,
} = require("@aws-sdk/client-lambda");
const {
  SFNClient,
  ListStateMachinesCommand,
} = require("@aws-sdk/client-sfn");
const {
  EventBridgeClient,
  ListEventBusesCommand,
} = require("@aws-sdk/client-eventbridge");
const {
  DynamoDBClient,
  ListTablesCommand,
} = require("@aws-sdk/client-dynamodb");
const {
  RDSClient,
  DescribeDBInstancesCommand,
  DescribeDBClustersCommand,
} = require("@aws-sdk/client-rds");
const {
  RedshiftClient,
  DescribeClustersCommand,
} = require("@aws-sdk/client-redshift");
const {
  AthenaClient,
  ListWorkGroupsCommand,
} = require("@aws-sdk/client-athena");
const {
  GlueClient,
  GetDatabasesCommand,
} = require("@aws-sdk/client-glue");
const {
  SageMakerClient,
  ListNotebookInstancesCommand,
} = require("@aws-sdk/client-sagemaker");
const {
  TextractClient,
} = require("@aws-sdk/client-textract");
const {
  RekognitionClient,
} = require("@aws-sdk/client-rekognition");
const {
  TranslateClient,
} = require("@aws-sdk/client-translate");
const {
  PollyClient,
} = require("@aws-sdk/client-polly");
const {
  ElasticacheClient,
  DescribeCacheClustersCommand,
} = require("@aws-sdk/client-elasticache");
const {
  DAXClient,
} = require("@aws-sdk/client-dax");
const {
  MemoryDBClient,
} = require("@aws-sdk/client-memorydb");
const {
  NeptuneClient,
} = require("@aws-sdk/client-neptune");
const {
const ec2Client = new EC2Client({});
const cloudFrontClient = new CloudFrontClient({});
const elbv2Client = new ELBv2Client({});
const route53ResolverClient = new Route53ResolverClient({});
const cloudWatchClient = new CloudWatchClient({});
const cloudWatchLogsClient = new CloudWatchLogsClient({});
const s3Client = new S3Client({});
const iamClient = new IAMClient({});
const organizationsClient = new OrganizationsClient({});
const stsClient = new STSClient({});
const kmsClient = new KMSClient({});
const secretsManagerClient = new SecretsManagerClient({});
const ssmClient = new SSMClient({});
const sqsClient = new SQSClient({});
const snsClient = new SNSClient({});
const lambdaClient = new LambdaClient({});
const sfnClient = new SFNClient({});
const eventBridgeClient = new EventBridgeClient({});
const dynamoDBClient = new DynamoDBClient({});
const rdsClient = new RDSClient({});
const redshiftClient = new RedshiftClient({});
const athenaClient = new AthenaClient({});
const glueClient = new GlueClient({});
const sagemakerClient = new SageMakerClient({});
const textractClient = new TextractClient({});
const rekognitionClient = new RekognitionClient({});
const translateClient = new TranslateClient({});
const pollyClient = new PollyClient({});
const elasticacheClient = new ElasticacheClient({});
const daxClient = new DAXClient({});
const memoryDBClient = new MemoryDBClient({});
const neptuneClient = new NeptuneClient({});

// Create MCP server
const server = new Server(
  {
    name: "aws-networking-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      resources: {},
    },
  }
);

// Set up resource listing handler
server.setRequestHandler(ListResourcesRequest, async () => {
  return {
    resources: [
      // EC2 Resources
      {
        uri: "aws://ec2/vpcs",
        name: "VPCs",
        description: "List of VPCs in the current region",
        mimeType: "application/json",
      },
      {
        uri: "aws://ec2/subnets",
        name: "Subnets",
        description: "List of subnets in the current region",
        mimeType: "application/json",
      },
      {
        uri: "aws://ec2/route-tables",
        name: "Route Tables",
        description: "List of route tables in the current region",
        mimeType: "application/json",
      },
      {
        uri: "aws://ec2/internet-gateways",
        name: "Internet Gateways",
        description: "List of internet gateways in the current region",
        mimeType: "application/json",
      },
      {
        uri: "aws://ec2/nat-gateways",
        name: "NAT Gateways",
        description: "List of NAT gateways in the current region",
        mimeType: "application/json",
      },
      {
        uri: "aws://ec2/security-groups",
        name: "Security Groups",
        description: "List of security groups in the current region",
        mimeType: "application/json",
      },
      // CloudFront Resources
      {
        uri: "aws://cloudfront/distributions",
        name: "CloudFront Distributions",
        description: "List of CloudFront distributions",
        mimeType: "application/json",
      },
      // Load Balancer Resources
      {
        uri: "aws://elbv2/load-balancers",
        name: "Load Balancers",
        description: "List of load balancers",
        mimeType: "application/json",
      },
      {
        uri: "aws://elbv2/target-groups",
        name: "Target Groups",
        description: "List of target groups",
        mimeType: "application/json",
      },
      {
        uri: "aws://elbv2/listeners",
        name: "Listeners",
        description: "List of listeners",
        mimeType: "application/json",
      },
      {
        uri: "aws://elbv2/rules",
        name: "Listener Rules",
        description: "List of listener rules",
        mimeType: "application/json",
      },
      // Route 53 Resources
      {
        uri: "aws://route53/resolver-endpoints",
        name: "Resolver Endpoints",
        description: "List of Route 53 Resolver endpoints",
        mimeType: "application/json",
      },
      {
        uri: "aws://route53/resolver-rules",
        name: "Resolver Rules",
        description: "List of Route 53 Resolver rules",
        mimeType: "application/json",
      },
      // CloudWatch Resources
      {
        uri: "aws://cloudwatch/metrics",
        name: "CloudWatch Metrics",
        description: "List of CloudWatch metrics",
        mimeType: "application/json",
      },
      {
        uri: "aws://cloudwatch/log-groups",
        name: "CloudWatch Log Groups",
        description: "List of CloudWatch log groups",
        mimeType: "application/json",
      },
      // S3 Resources
      {
        uri: "aws://s3/buckets",
        name: "S3 Buckets",
        description: "List of S3 buckets",
        mimeType: "application/json",
      },
      {
        uri: "aws://s3/objects",
        name: "S3 Objects",
        description: "List of objects in S3 buckets",
        mimeType: "application/json",
      },
      // IAM Resources
      {
        uri: "aws://iam/users",
        name: "IAM Users",
        description: "List of IAM users",
        mimeType: "application/json",
      },
      {
        uri: "aws://iam/roles",
        name: "IAM Roles",
        description: "List of IAM roles",
        mimeType: "application/json",
      },
      {
        uri: "aws://iam/policies",
        name: "IAM Policies",
        description: "List of IAM policies",
        mimeType: "application/json",
      },
      // Organizations Resources
      {
        uri: "aws://organizations/accounts",
        name: "Organization Accounts",
        description: "List of accounts in the organization",
        mimeType: "application/json",
      },
      {
        uri: "aws://organizations/organizational-units",
        name: "Organizational Units",
        description: "List of organizational units",
        mimeType: "application/json",
      },
      // STS Resources
      {
        uri: "aws://sts/caller-identity",
        name: "Caller Identity",
        description: "Information about the caller identity",
        mimeType: "application/json",
      },
      // KMS Resources
      {
        uri: "aws://kms/keys",
        name: "KMS Keys",
        description: "List of KMS keys",
        mimeType: "application/json",
      },
      // Secrets Manager Resources
      {
        uri: "aws://secrets-manager/secrets",
        name: "Secrets",
        description: "List of secrets",
        mimeType: "application/json",
      },
      // SSM Resources
      {
        uri: "aws://ssm/parameters",
        name: "Parameters",
        description: "List of SSM parameters",
        mimeType: "application/json",
      },
      // SQS Resources
      {
        uri: "aws://sqs/queues",
        name: "SQS Queues",
        description: "List of SQS queues",
        mimeType: "application/json",
      },
      // SNS Resources
      {
        uri: "aws://sns/topics",
        name: "SNS Topics",
        description: "List of SNS topics",
        mimeType: "application/json",
      },
      // Lambda Resources
      {
        uri: "aws://lambda/functions",
        name: "Lambda Functions",
        description: "List of Lambda functions",
        mimeType: "application/json",
      },
      // Step Functions Resources
      {
        uri: "aws://sfn/state-machines",
        name: "State Machines",
        description: "List of Step Functions state machines",
        mimeType: "application/json",
      },
      // EventBridge Resources
      {
        uri: "aws://eventbridge/event-buses",
        name: "Event Buses",
        description: "List of EventBridge event buses",
        mimeType: "application/json",
      },
      // DynamoDB Resources
      {
        uri: "aws://dynamodb/tables",
        name: "DynamoDB Tables",
        description: "List of DynamoDB tables",
        mimeType: "application/json",
      },
      // RDS Resources
      {
        uri: "aws://rds/db-instances",
        name: "RDS DB Instances",
        description: "List of RDS database instances",
        mimeType: "application/json",
      },
      {
        uri: "aws://rds/db-clusters",
        name: "RDS DB Clusters",
        description: "List of RDS database clusters",
        mimeType: "application/json",
      },
      // Redshift Resources
      {
        uri: "aws://redshift/clusters",
        name: "Redshift Clusters",
        description: "List of Redshift clusters",
        mimeType: "application/json",
      },
      // Athena Resources
      {
        uri: "aws://athena/work-groups",
        name: "Athena Work Groups",
        description: "List of Athena work groups",
        mimeType: "application/json",
      },
      // Glue Resources
      {
        uri: "aws://glue/databases",
        name: "Glue Databases",
        description: "List of Glue databases",
        mimeType: "application/json",
      },
      // SageMaker Resources
      {
        uri: "aws://sagemaker/notebook-instances",
        name: "SageMaker Notebook Instances",
        description: "List of SageMaker notebook instances",
        mimeType: "application/json",
      },
      // Textract Resources
      {
        uri: "aws://textract",
        name: "Textract",
        description: "Textract service",
        mimeType: "application/json",
      },
      // Rekognition Resources
      {
        uri: "aws://rekognition",
        name: "Rekognition",
        description: "Rekognition service",
        mimeType: "application/json",
      },
      // Translate Resources
      {
        uri: "aws://translate",
        name: "Translate",
        description: "Translate service",
        mimeType: "application/json",
      },
      // Polly Resources
      {
        uri: "aws://polly",
        name: "Polly",
        description: "Polly service",
        mimeType: "application/json",
      },
      // ElastiCache Resources
      {
        uri: "aws://elasticache/clusters",
        name: "ElastiCache Clusters",
        description: "List of ElastiCache clusters",
        mimeType: "application/json",
      },
      // DAX Resources
      {
        uri: "aws://dax",
        name: "DAX",
        description: "DAX service",
        mimeType: "application/json",
      },
      // MemoryDB Resources
      {
        uri: "aws://memorydb",
        name: "MemoryDB",
        description: "MemoryDB service",
        mimeType: "application/json",
      },
      // Neptune Resources
      {
        uri: "aws://neptune",
        name: "Neptune",
        description: "Neptune service",
        mimeType: "application/json",
      },
    ],
  };
});

// Set up resource reading handler
server.setRequestHandler(ReadResourceRequest, async (request) => {
  const uri = request.params.uri;
  
  try {
    // EC2 Resources
    if (uri === "aws://ec2/vpcs") {
      const command = new DescribeVpcsCommand({});
      const response = await ec2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Vpcs, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://ec2/subnets") {
      const command = new DescribeSubnetsCommand({});
      const response = await ec2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Subnets, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://ec2/route-tables") {
      const command = new DescribeRouteTablesCommand({});
      const response = await ec2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.RouteTables, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://ec2/internet-gateways") {
      const command = new DescribeInternetGatewaysCommand({});
      const response = await ec2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.InternetGateways, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://ec2/nat-gateways") {
      const command = new DescribeNatGatewaysCommand({});
      const response = await ec2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.NatGateways, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://ec2/security-groups") {
      const command = new DescribeSecurityGroupsCommand({});
      const response = await ec2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.SecurityGroups, null, 2),
          },
        ],
      };
    }
    
    // CloudFront Resources
    if (uri === "aws://cloudfront/distributions") {
      const command = new ListDistributionsCommand({});
      const response = await cloudFrontClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.DistributionList?.Items || [], null, 2),
          },
        ],
      };
    }
    
    // Load Balancer Resources
    if (uri === "aws://elbv2/load-balancers") {
      const command = new DescribeLoadBalancersCommand({});
      const response = await elbv2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.LoadBalancers, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://elbv2/target-groups") {
      const command = new DescribeTargetGroupsCommand({});
      const response = await elbv2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.TargetGroups, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://elbv2/listeners") {
      const command = new DescribeListenersCommand({});
      const response = await elbv2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Listeners, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://elbv2/rules") {
      const command = new DescribeRulesCommand({});
      const response = await elbv2Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Rules, null, 2),
          },
        ],
      };
    }
    
    // Route 53 Resources
    if (uri === "aws://route53/resolver-endpoints") {
      const command = new ListResolverEndpointsCommand({});
      const response = await route53ResolverClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.ResolverEndpoints, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://route53/resolver-rules") {
      const command = new ListResolverRulesCommand({});
      const response = await route53ResolverClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.ResolverRules, null, 2),
          },
        ],
      };
    }
    
    // CloudWatch Resources
    if (uri === "aws://cloudwatch/metrics") {
      const command = new ListMetricsCommand({});
      const response = await cloudWatchClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Metrics, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://cloudwatch/log-groups") {
      const command = new DescribeLogGroupsCommand({});
      const response = await cloudWatchLogsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.LogGroups, null, 2),
          },
        ],
      };
    }
    
    // S3 Resources
    if (uri === "aws://s3/buckets") {
      const command = new ListBucketsCommand({});
      const response = await s3Client.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Buckets, null, 2),
          },
        ],
      };
    }
    
    // IAM Resources
    if (uri === "aws://iam/users") {
      const command = new ListUsersCommand({});
      const response = await iamClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Users, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://iam/roles") {
      const command = new ListRolesCommand({});
      const response = await iamClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Roles, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://iam/policies") {
      const command = new ListPoliciesCommand({});
      const response = await iamClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Policies, null, 2),
          },
        ],
      };
    }
    
    // Organizations Resources
    if (uri === "aws://organizations/accounts") {
      const command = new ListAccountsCommand({});
      const response = await organizationsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Accounts, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://organizations/organizational-units") {
      // This requires a parent ID, so we'll return an empty array for now
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify([], null, 2),
          },
        ],
      };
    }
    
    // STS Resources
    if (uri === "aws://sts/caller-identity") {
      const command = new GetCallerIdentityCommand({});
      const response = await stsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response, null, 2),
          },
        ],
      };
    }
    
    // KMS Resources
    if (uri === "aws://kms/keys") {
      const command = new ListKeysCommand({});
      const response = await kmsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Keys, null, 2),
          },
        ],
      };
    }
    
    // Secrets Manager Resources
    if (uri === "aws://secrets-manager/secrets") {
      const command = new ListSecretsCommand({});
      const response = await secretsManagerClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.SecretList, null, 2),
          },
        ],
      };
    }
    
    // SSM Resources
    if (uri === "aws://ssm/parameters") {
      const command = new DescribeParametersCommand({});
      const response = await ssmClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Parameters, null, 2),
          },
        ],
      };
    }
    
    // SQS Resources
    if (uri === "aws://sqs/queues") {
      const command = new ListQueuesCommand({});
      const response = await sqsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.QueueUrls, null, 2),
          },
        ],
      };
    }
    
    // SNS Resources
    if (uri === "aws://sns/topics") {
      const command = new ListTopicsCommand({});
      const response = await snsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Topics, null, 2),
          },
        ],
      };
    }
    
    // Lambda Resources
    if (uri === "aws://lambda/functions") {
      const command = new ListFunctionsCommand({});
      const response = await lambdaClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Functions, null, 2),
          },
        ],
      };
    }
    
    // Step Functions Resources
    if (uri === "aws://sfn/state-machines") {
      const command = new ListStateMachinesCommand({});
      const response = await sfnClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.StateMachines, null, 2),
          },
        ],
      };
    }
    
    // EventBridge Resources
    if (uri === "aws://eventbridge/event-buses") {
      const command = new ListEventBusesCommand({});
      const response = await eventBridgeClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.EventBuses, null, 2),
          },
        ],
      };
    }
    
    // DynamoDB Resources
    if (uri === "aws://dynamodb/tables") {
      const command = new ListTablesCommand({});
      const response = await dynamoDBClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.TableNames, null, 2),
          },
        ],
      };
    }
    
    // RDS Resources
    if (uri === "aws://rds/db-instances") {
      const command = new DescribeDBInstancesCommand({});
      const response = await rdsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.DBInstances, null, 2),
          },
        ],
      };
    }
    
    if (uri === "aws://rds/db-clusters") {
      const command = new DescribeDBClustersCommand({});
      const response = await rdsClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.DBClusters, null, 2),
          },
        ],
      };
    }
    
    // Redshift Resources
    if (uri === "aws://redshift/clusters") {
      const command = new DescribeClustersCommand({});
      const response = await redshiftClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.Clusters, null, 2),
          },
        ],
      };
    }
    
    // Athena Resources
    if (uri === "aws://athena/work-groups") {
      const command = new ListWorkGroupsCommand({});
      const response = await athenaClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.WorkGroups, null, 2),
          },
        ],
      };
    }
    
    // Glue Resources
    if (uri === "aws://glue/databases") {
      const command = new GetDatabasesCommand({});
      const response = await glueClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.DatabaseList, null, 2),
          },
        ],
      };
    }
    
    // SageMaker Resources
    if (uri === "aws://sagemaker/notebook-instances") {
      const command = new ListNotebookInstancesCommand({});
      const response = await sagemakerClient.send(command);
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(response.NotebookInstances, null, 2),
          },
        ],
      };
    }
    
    // Default response for unimplemented resources
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({ error: "Resource not implemented" }, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify({ error: error.message }, null, 2),
        },
      ],
    };
  }
});

// Set up resource templates handler
server.setRequestHandler(ListResourceTemplatesRequest, async () => {
  return {
    resourceTemplates: [],
  };
});

// Start the server
async function startServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("AWS Networking MCP Server running on stdio");
}

startServer().catch((error) => {
  console.error("Failed to start server:", error);
  process.exit(1);
});
