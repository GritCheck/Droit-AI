import type { BoxProps } from '@mui/material/Box';
import type { CardProps } from '@mui/material/Card';

import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Stack from '@mui/material/Stack';
import CardHeader from '@mui/material/CardHeader';
import Typography from '@mui/material/Typography';

import { fDate } from 'src/utils/format-time';

import { Label } from 'src/components/label';
import { Iconify } from 'src/components/iconify';
import { Scrollbar } from 'src/components/scrollbar';

// ----------------------------------------------------------------------

export interface GroundednessTrendItem {
  id: string;
  date: string;
  score: number;
  category: string;
  image: null;
  postedAt: string;
}

// ----------------------------------------------------------------------

type Props = CardProps & {
  title?: string;
  subheader?: string;
  list: GroundednessTrendItem[];
};

export function AppTopRelated({ title, subheader, list, sx, ...other }: Props) {

  return (
    <Card sx={sx} {...other}>
      <CardHeader title={title} subheader={subheader} sx={{ mb: 3 }} />

      <Scrollbar sx={{ minHeight: 384 }}>
        <Box
          sx={{
            p: 3,
            gap: 3,
            minWidth: 360,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {list.map((item) => (
            <Item key={item.id} item={item} />
          ))}
        </Box>
      </Scrollbar>
    </Card>
  );
}

// ----------------------------------------------------------------------

type ItemProps = BoxProps & {
  item: Props['list'][number];
};

function Item({ item, sx, ...other }: ItemProps) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 80) return 'warning';
    return 'error';
  };

  return (
    <Box
      sx={[{ gap: 2, display: 'flex', alignItems: 'center' }, ...(Array.isArray(sx) ? sx : [sx])]}
      {...other}
    >
      <div>
        <Box
          sx={{
            mb: 1,
            gap: 1,
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Typography variant="subtitle2" noWrap>
            {fDate(item.date)}
          </Typography>

          <Label color={getScoreColor(item.score)} sx={{ height: 20 }}>
            {item.score}%
          </Label>
        </Box>

        <Stack
          divider={
            <Box
              sx={{
                width: 4,
                height: 4,
                borderRadius: '50%',
                bgcolor: 'text.disabled',
              }}
            />
          }
          sx={{
            gap: 1,
            flexDirection: 'row',
            alignItems: 'center',
            typography: 'caption',
          }}
        >
          <Box sx={{ gap: 0.5, display: 'flex', alignItems: 'center' }}>
            <Iconify width={16} icon="solar:chart-square-bold" sx={{ color: 'text.disabled' }} />
            {item.category}
          </Box>

          <Box sx={{ gap: 0.5, display: 'flex', alignItems: 'center' }}>
            <Iconify width={16} icon="solar:calendar-bold" sx={{ color: 'text.disabled' }} />
            {item.date}
          </Box>

          <Box sx={{ gap: 0.5, display: 'flex', alignItems: 'center' }}>
            <Iconify width={16} icon="solar:target-bold" sx={{ color: 'text.disabled' }} />
            Score: {item.score}
          </Box>
        </Stack>
      </div>
    </Box>
  );
}
