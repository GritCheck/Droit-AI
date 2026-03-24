import type { Metadata } from 'next';

import { kebabCase } from 'es-toolkit';

import { CONFIG } from 'src/global-config';
import axios, { endpoints } from 'src/lib/axios';

import { PostDetailsHomeView } from 'src/sections/blog/view';

// ----------------------------------------------------------------------

export const metadata: Metadata = { title: `Post details - ${CONFIG.appName}` };

type Props = {
  params: { title: string };
};

async function getPost(title: string) {
  // Ensure we handle the case where title might be empty/null
  const URL = title ? `${endpoints.post.details}?title=${title}` : '';

  const res = await axios.get(URL);

  return res.data;
}

export default async function Page({ params }: Props) {
  const { title } = params;

  const { post } = await getPost(title);

  const { latestPosts } = await getPost(title);

  return <PostDetailsHomeView post={post} latestPosts={latestPosts} />;
}

// ----------------------------------------------------------------------

/**
 * [1] Default
 * Remove [1] and [2] if not using [2]
 * Will remove in Next.js v15
 */
export const dynamic = 'force-dynamic';

/**
 * [2] Static exports
 * https://nextjs.org/docs/app/building-your-application/deploying/static-exports
 */
export async function generateStaticParams() {
  if (CONFIG.isStaticExport) {
    const res = await axios.get(endpoints.post.list);
    return res.data.posts.map((post: { title: string }) => ({ title: kebabCase(post.title) }));
  }
  return [];
}
