import type { BoxProps } from '@mui/material/Box';

import { useState } from 'react';
import { m } from 'framer-motion';
import { varAlpha } from 'minimal-shared/utils';

import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Accordion, { accordionClasses } from '@mui/material/Accordion';
import AccordionDetails, { accordionDetailsClasses } from '@mui/material/AccordionDetails';
import AccordionSummary, { accordionSummaryClasses } from '@mui/material/AccordionSummary';

import { Iconify } from 'src/components/iconify';
import { varFade, MotionViewport } from 'src/components/animate';

import { SectionTitle } from './components/section-title';
import { FloatLine, FloatPlusIcon, FloatTriangleDownIcon } from './components/svg-elements';

// ----------------------------------------------------------------------

const FAQs = [
  {
    question: 'How does SentinelRAG ensure answer accuracy?',
    answer: (
      <Typography>
        SentinelRAG uses Azure AI Search with semantic ranking and hybrid vector capabilities. Every answer includes verifiable citations with exact page numbers and source references. Our responsible AI framework includes groundedness scoring using Azure AI Studio evaluators to ensure factual accuracy.
      </Typography>
    ),
  },
  {
    question: 'Which SentinelRAG plan is right for my organization?',
    answer: (
      <Box component="ul" sx={{ pl: 3, listStyleType: 'disc' }}>
        <li><strong>Starter Plan</strong>: Ideal for small teams, up to 1K documents (Basic Azure AI Search)</li>
        <li><strong>Professional Plan</strong>: Perfect for growing organizations, up to 10K documents (Advanced semantic search)</li>
        <li><strong>Enterprise Plan</strong>: Best for large enterprises, unlimited documents (Dedicated Azure resources)</li>
        <li>All plans include Azure AD integration and real-time citations</li>
        <li>
          Use our
          <Link
            href="/demo"
            sx={{ mx: 0.5, cursor: 'pointer' }}
          >
            free demo
          </Link>
          to test capabilities with your documents
        </li>
      </Box>
    ),
  },
  {
    question: 'What is the implementation process?',
    answer: (
      <Box component="ul" sx={{ pl: 3, listStyleType: 'disc' }}>
        <li>Submit your requirements and schedule Azure environment setup</li>
        <li>Configure Azure AI Search and integrate your document sources</li>
        <li>Set up Azure AD authentication and role-based access</li>
        <li>Test with your documents and train custom models if needed</li>
        <li>Go live with enterprise-grade RAG capabilities</li>
      </Box>
    ),
  },
  {
    question: 'How secure is our data with SentinelRAG?',
    answer: (
      <Typography>
        SentinelRAG is built on Azure's enterprise-grade security infrastructure. All data is encrypted at rest and in transit, with Azure AD integration for identity management. We provide complete audit trails in Azure Cosmos DB and comply with enterprise security standards. Your documents never leave your Azure tenant.
      </Typography>
    ),
  },
  {
    question: 'Do you offer enterprise solutions?',
    answer: (
      <Typography>
        Yes! We provide dedicated enterprise RAG solutions with custom AI models, dedicated Azure resources, and 24/7 enterprise support. Our Azure-first architecture ensures seamless integration with your existing enterprise systems and compliance requirements.
      </Typography>
    ),
  },
  {
    question: 'Do you have a free demo to review before purchasing?',
    answer: (
      <Typography>
        Yes, you can check out our
        <Link
          href="https://mui.com/store/items/sentinelrag-dashboard-free/"
          target="_blank"
          rel="noopener"
          sx={{ mx: 0.5 }}
        >
          open source
        </Link>
        dashboard template which should give you an overview of the RAG capabilities and Azure integration. Keep in mind that some enterprise features may differ from this version.
      </Typography>
    ),
  },
];

// ----------------------------------------------------------------------

export function HomeFAQs({ sx, ...other }: BoxProps) {
  const [expanded, setExpanded] = useState<string | false>(FAQs[0].question);

  const handleChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  const renderDescription = () => (
    <SectionTitle
      caption="FAQs"
      title="We’ve got the"
      txtGradient="answers"
      sx={{ textAlign: 'center' }}
    />
  );

  const renderContent = () => (
    <Stack
      spacing={1}
      sx={[
        () => ({
          mt: 8,
          mx: 'auto',
          maxWidth: 720,
          mb: { xs: 5, md: 8 },
        }),
      ]}
    >
      {FAQs.map((item, index) => (
        <Accordion
          key={item.question}
          component={m.div}
          variants={varFade('inUp', { distance: 24 })}
          expanded={expanded === item.question}
          onChange={handleChange(item.question)}
          sx={(theme) => ({
            borderRadius: 2,
            transition: theme.transitions.create(['background-color'], {
              duration: theme.transitions.duration.short,
            }),
            '&::before': { display: 'none' },
            '&:hover': { bgcolor: varAlpha(theme.vars.palette.grey['500Channel'], 0.16) },
            '&:first-of-type, &:last-of-type': { borderRadius: 2 },
            [`&.${accordionClasses.expanded}`]: {
              m: 0,
              borderRadius: 2,
              boxShadow: 'none',
              bgcolor: varAlpha(theme.vars.palette.grey['500Channel'], 0.08),
            },
            [`& .${accordionSummaryClasses.root}`]: {
              py: 3,
              px: 2.5,
              minHeight: 'auto',
              [`& .${accordionSummaryClasses.content}`]: {
                m: 0,
                [`&.${accordionSummaryClasses.expanded}`]: { m: 0 },
              },
            },
            [`& .${accordionDetailsClasses.root}`]: { px: 2.5, pt: 0, pb: 3 },
          })}
        >
          <AccordionSummary
            expandIcon={
              <Iconify
                width={20}
                icon={expanded === item.question ? 'mingcute:minimize-line' : 'mingcute:add-line'}
              />
            }
            aria-controls={`panel${index}bh-content`}
            id={`panel${index}bh-header`}
          >
            <Typography variant="h6"> {item.question}</Typography>
          </AccordionSummary>
          <AccordionDetails>{item.answer}</AccordionDetails>
        </Accordion>
      ))}
    </Stack>
  );

  const renderContact = () => (
    <Box
      sx={[
        (theme) => ({
          px: 3,
          py: 8,
          textAlign: 'center',
          background: `linear-gradient(to left, ${varAlpha(theme.vars.palette.grey['500Channel'], 0.08)}, transparent)`,
        }),
      ]}
    >
      <m.div variants={varFade('in')}>
        <Typography variant="h4">Still have questions?</Typography>
      </m.div>

      <m.div variants={varFade('in')}>
        <Typography sx={{ mt: 2, mb: 3, color: 'text.secondary' }}>
          Please describe your case to receive the most accurate advice
        </Typography>
      </m.div>

      <m.div variants={varFade('in')}>
        <Button
          color="inherit"
          variant="contained"
          href="mailto:support@sentinelrag.cc?subject=[Feedback] from Customer"
          startIcon={<Iconify icon="fluent:mail-24-filled" />}
        >
          Contact us
        </Button>
      </m.div>
    </Box>
  );

  return (
    <Box component="section" sx={sx} {...other}>
      <MotionViewport sx={{ py: 10, position: 'relative' }}>
        {topLines()}

        <Container>
          {renderDescription()}
          {renderContent()}
        </Container>

        <Stack sx={{ position: 'relative' }}>
          {bottomLines()}
          {renderContact()}
        </Stack>
      </MotionViewport>
    </Box>
  );
}

// ----------------------------------------------------------------------

const topLines = () => (
  <>
    <Stack
      spacing={8}
      alignItems="center"
      sx={{
        top: 64,
        left: 80,
        position: 'absolute',
        transform: 'translateX(-50%)',
      }}
    >
      <FloatTriangleDownIcon sx={{ position: 'static', opacity: 0.12 }} />
      <FloatTriangleDownIcon
        sx={{
          width: 30,
          height: 15,
          opacity: 0.24,
          position: 'static',
        }}
      />
    </Stack>

    <FloatLine vertical sx={{ top: 0, left: 80 }} />
  </>
);

const bottomLines = () => (
  <>
    <FloatLine sx={{ top: 0, left: 0 }} />
    <FloatLine sx={{ bottom: 0, left: 0 }} />
    <FloatPlusIcon sx={{ top: -8, left: 72 }} />
    <FloatPlusIcon sx={{ bottom: -8, left: 72 }} />
  </>
);
