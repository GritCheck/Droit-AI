import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';
import axios, { endpoints } from 'src/lib/axios';

import { PostEditView } from 'src/sections/blog/view';

// ----------------------------------------------------------------------

type Props = {
  params: Promise<{ title: string }>; // Updated to Promise for Next.js 15/16
};

// Metadata must now await params
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { title } = await params;
  const displayTitle = title.replace(/-/g, ' '); // Simple formatting for the tab title

  return {
    title: `${displayTitle} | Dashboard - ${CONFIG.appName}`,
  };
}

export default async function Page({ params }: Props) {
  // NEXT.JS 16 FIX: Must await params before destructuring
  const { title } = await params;

  const { post } = await getPost(title);

  return <PostEditView post={post} />;
}

async function getPost(title: string) {
  const URL = title ? `${endpoints.post.details}?title=${title}` : '';

  const res = await axios.get(URL);

  return res.data;
}
